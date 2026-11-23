"""Flask app factory backed by the audited, transaction-safe booking service.

The browser supplies *only* resource IDs, reservation IDs and form fields.
Actor identity and role are always resolved from a server-signed session and DB.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps
import hmac
import os
from pathlib import Path
import secrets
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import (Flask, abort, flash, g, jsonify, make_response, redirect, render_template, request,
                   session, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import Session
from sqlalchemy import select

from unireserve.domain.availability import TimeWindow
from unireserve.domain.operating_hours import BAKU, open_at
from unireserve.services.booking import (
    AccessDenied, BookingService, Conflict, InvalidRequest, MissingRecord, BookingError,
)
from unireserve.storage.accounts import verify_password
from unireserve.storage.db import create_schema, make_engine
from unireserve.storage.models import User, Space


BASE_DIR = Path(__file__).resolve().parents[3]


def create_app(test_config: dict | None = None) -> Flask:
    """Create an isolated Flask application (supports test database injection)."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    mode = os.environ.get("UNIRESERVE_MODE", "local").strip().lower()
    if mode not in ("local", "production"):
        raise RuntimeError("UNIRESERVE_MODE must be local or production")
    production = mode == "production"
    configured_hosts = [h.strip() for h in os.environ.get("UNIRESERVE_TRUSTED_HOSTS", "").split(",") if h.strip()]

    app.config.update(
        SECRET_KEY=os.environ.get("UNIRESERVE_SECRET_KEY") or secrets.token_hex(32),
        DB_PATH=os.environ.get("UNIRESERVE_DB_PATH") or str(BASE_DIR / "instance" / "unireserve.sqlite3"),
        DISPLAY_TIMEZONE=os.environ.get("UNIRESERVE_TIMEZONE", "Asia/Baku"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=production,
        TRUSTED_HOSTS=configured_hosts if production else None,
        PRODUCTION_MODE=production,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        PREFERRED_URL_SCHEME="https" if production else "http",
        MAX_CONTENT_LENGTH=64 * 1024,
        AUTO_SAMPLE_CATALOG=None,  # explicitly enabled by the local demo launcher only
    )
    if test_config is not None:
        app.config.update(test_config)
    if production and os.environ.get("UNIRESERVE_PROXY_COUNT"):
        proxy_count = int(os.environ["UNIRESERVE_PROXY_COUNT"])
        if not 1 <= proxy_count <= 3:
            raise RuntimeError("UNIRESERVE_PROXY_COUNT must be between 1 and 3")
        # Enable only behind the exact number of trusted reverse proxies.
        # The reverse proxy must replace forwarded headers from clients.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=proxy_count, x_host=proxy_count)
    if app.config["AUTO_SAMPLE_CATALOG"] is None:
        app.config["AUTO_SAMPLE_CATALOG"] = os.environ.get("UNIRESERVE_AUTO_SAMPLE_CATALOG", "0") == "1"
    if app.config["PRODUCTION_MODE"]:
        if (len(str(app.config.get("SECRET_KEY") or "")) < 32 or not os.environ.get("UNIRESERVE_SECRET_KEY") or str(app.config["SECRET_KEY"]).startswith("REPLACE_")):
            raise RuntimeError("Production requires a stable UNIRESERVE_SECRET_KEY of at least 32 characters")
        if not app.config.get("TRUSTED_HOSTS"):
            raise RuntimeError("Production requires UNIRESERVE_TRUSTED_HOSTS")
        if not app.config.get("SESSION_COOKIE_SECURE"):
            raise RuntimeError("Production requires HTTPS-only session cookies")
        if app.config["AUTO_SAMPLE_CATALOG"]:
            raise RuntimeError("Automatic sample catalogue initialization is disabled in production")
    try:
        display_zone = ZoneInfo(app.config["DISPLAY_TIMEZONE"])
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError("Invalid UNIRESERVE_TIMEZONE; install tzdata if required") from exc
    engine = make_engine(app.config["DB_PATH"])
    create_schema(engine)
    # CR-004: local demo entry point opts into a one-time idempotent sample sync.
    # Existing bookings, users, audit events and admin-created resources persist.
    # API/test factories do not auto-seed unless explicitly configured.
    if app.config["AUTO_SAMPLE_CATALOG"]:
        from unireserve.storage.aztu_demo import sync_demo_catalog
        with Session(engine) as db:
            missing_demo_areas = db.scalar(select(Space.id).limit(1)) is None
        if missing_demo_areas:
            sync_demo_catalog(engine)
    service = BookingService(engine)
    app.extensions["unireserve_engine"] = engine

    @app.template_filter("area_title")
    def area_title(value):
        if not value:
            return ""
        return (str(value)
                .replace("AzTU Library · ", "Library · ")
                .replace(" (demo)", "")
                .replace(" (sample)", ""))

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'")
        if request.path.startswith("/static/"):
            response.headers.setdefault("Cache-Control", "public, max-age=3600")
        else:
            response.headers["Cache-Control"] = "no-store"
        if app.config["PRODUCTION_MODE"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    def actor_id() -> int:
        """Only trusted data from the signed Flask session supplies identity."""
        if g.user is None:
            raise AccessDenied("authentication is required")
        return g.user.id

    @app.before_request
    def load_user_and_check_csrf():
        g.user = None
        uid = session.get("uid")
        if type(uid) is int:
            with Session(engine) as db:
                user = db.get(User, uid)
                if user is not None and user.is_active:
                    g.user = user
                else:
                    session.pop("uid", None)
        if request.method == "POST":
            expected = session.get("csrf_token", "")
            actual = request.form.get("csrf_token", "")
            if not expected or not hmac.compare_digest(expected, actual):
                abort(400, description="Invalid or expired form token. Refresh the page and retry.")

    @app.context_processor
    def template_helpers():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)

        def local_time(dt: datetime | None) -> str:
            if dt is None:
                return "—"
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(display_zone).strftime("%d %b %Y · %H:%M")

        return {
            "csrf_token": session["csrf_token"],
            "local_time": local_time,
            "timezone_name": app.config["DISPLAY_TIMEZONE"],
            "current_year": datetime.now().year,
        }

    def login_required(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if g.user is None:
                return redirect(url_for("login"))
            return fn(*args, **kwargs)
        return wrapped

    def admin_required(fn):
        @wraps(fn)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user.role != "ADMIN":
                abort(403)
            return fn(*args, **kwargs)
        return wrapped

    def resolve_error(exc: BookingError, fallback: str):
        if isinstance(exc, AccessDenied):
            abort(403)
        if isinstance(exc, MissingRecord):
            abort(404)
        flash(str(exc), "error")
        return redirect(fallback)

    def form_window() -> TimeWindow:
        try:
            # A datetime-local field has no timezone. Treat the user-entered
            # wall time as the configured university timezone; show this in UI.
            start = datetime.strptime(request.form["start"], "%Y-%m-%dT%H:%M").replace(tzinfo=display_zone)
            end = datetime.strptime(request.form["end"], "%Y-%m-%dT%H:%M").replace(tzinfo=display_zone)
            return TimeWindow(start, end)
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidRequest("Enter valid start and end times (end must be after start).") from exc

    def time_suggestions(space=None):
        local_now = datetime.now(display_zone)
        start = (local_now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        # Always at least 1h in the future.
        if start <= local_now:
            start += timedelta(hours=1)
        if space is not None:
            from datetime import time
            days = {int(x) for x in space.open_days.split(",") if x.strip()}
            # Next safe, bookable local hour: not necessarily the present hour.
            for _ in range(16):
                if start.weekday() in days and space.is_enabled:
                    opening = datetime.combine(start.date(), time.fromisoformat(space.opens_at), display_zone)
                    closing = datetime.combine(start.date(), time.fromisoformat(space.closes_at), display_zone)
                    start = max(start, opening)
                    if start + timedelta(hours=1) <= closing:
                        break
                start = datetime.combine(start.date() + timedelta(days=1),
                                         time.fromisoformat(space.opens_at), display_zone)
        end = start + timedelta(hours=1)
        return start.strftime("%Y-%m-%dT%H:%M"), end.strftime("%Y-%m-%dT%H:%M")

    @app.get("/")
    def index():
        return redirect(url_for("resources") if g.user else url_for("login"))

    @app.get("/about")
    def about():
        return render_template("about.html", page_title="Service information")

    @app.get("/healthz")
    def healthz():
        try:
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
        except Exception:
            return jsonify({"status": "unavailable"}), 503
        return jsonify({"status": "ok"})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if g.user is not None:
            return redirect(url_for("resources"))
        if request.method == "POST":
            email = request.form.get("email", "").strip().casefold()
            password = request.form.get("password", "")
            with Session(engine) as db:
                user = db.scalar(select(User).where(User.email == email))
                if user is not None and user.is_active and verify_password(password, user.password_hash):
                    session.clear()
                    session["uid"] = user.id
                    session["csrf_token"] = secrets.token_urlsafe(32)
                    flash("Welcome back. You're signed in.", "success")
                    return redirect(url_for("resources"))
            flash("Incorrect email or password.", "error")
        return render_template("login.html", page_title="Sign in")

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        flash("You have signed out.", "success")
        return redirect(url_for("login"))

    def display_status(st):
        if st is None:
            return "UNKNOWN"
        return st.state

    @app.context_processor
    def image_and_status_helpers():
        def resource_photo(resource):
            code = resource.public_code.upper()
            # Match a photograph to the actual demo bookable area, not to
            # generic "ROOM" or "EQUIPMENT" database categories.
            for prefix, css in (
                ("AZ-LS-", "photo-library-seats"),
                ("AZ-LP-", "photo-library-pcs"),
                ("AZ-CP-", "photo-teaching-lab"),
                ("AZ-GR-", "photo-group-study"),
            ):
                if code.startswith(prefix):
                    return css
            name = (resource.name + " " + code).casefold()
            return "photo-lab" if any(word in name for word in ("pc", "workstation", "computer")) else "photo-study"
        return {"resource_photo": resource_photo, "display_status": display_status}

    def studio_groups(resources, spaces, statuses):
        """Stable, illustrative seat plans grouped by bookable area."""
        groups = []
        for space in spaces:
            items = sorted((r for r in resources if r.space_id == space.id), key=lambda r: r.public_code)
            if not items:
                continue
            # Visual template arranges units into two desk banks with an aisle.
            # Physical positions are an explicit demo design, not surveyed AzTU data.
            points = [
                {"resource": resource, "status": statuses[resource.id]}
                for resource in items
            ]
            groups.append({"space": space, "points": points, "count": len(items)})
        return groups

    @app.get("/studio")
    @login_required
    def studio():
        resources = service.list_resources(actor_id())
        statuses = service.status_overview(actor_id())
        spaces = service.list_spaces(actor_id())
        return render_template("studio.html", page_title="Choose a seat or PC",
                               groups=studio_groups(resources, spaces, statuses),
                               resources=resources, statuses=statuses,
                               checked_time=datetime.now(display_zone).strftime("%H:%M"))

    @app.get("/api/availability-status")
    @login_required
    def availability_status_json():
        """Informational read-only snapshot; never exposes reservation owners."""
        statuses = service.status_overview(actor_id())
        response = make_response(jsonify({
            "checked_at": datetime.now(display_zone).strftime("%H:%M"),
            "timezone": app.config["DISPLAY_TIMEZONE"],
            "resources": {str(resource_id): {
                "state": status.state,
                "next_start": status.next_start.isoformat() if status.next_start else None,
                "current_end": status.current_end.isoformat() if status.current_end else None,
            } for resource_id, status in statuses.items()}
        }))
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/resources")
    @login_required
    def resources():
        records = service.list_resources(actor_id())
        category = request.args.get("category", "ALL").upper()
        if category not in ("ALL", "ROOM", "EQUIPMENT", "SEAT", "PC", "LAB", "STUDY"):
            category = "ALL"
        term = request.args.get("q", "").strip()[:100]
        spaces = {s.id: s for s in service.list_spaces(actor_id())}
        def matches_category(r):
            kind = spaces[r.space_id].kind if r.space_id in spaces else ""
            return (category == "ALL" or r.category == category
                    or (category == "SEAT" and kind == "LIBRARY_SEAT")
                    or (category == "PC" and kind in ("LIBRARY_PC", "COMPUTER_LAB"))
                    or (category == "LAB" and kind == "COMPUTER_LAB")
                    or (category == "STUDY" and kind == "STUDY_ROOM"))
        visible = [r for r in records if matches_category(r)
                   and (not term or term.casefold() in (r.name + " " + r.public_code).casefold())]
        statuses = service.status_overview(actor_id())
        area_images = {
            "LIBRARY_SEAT": "library-seats.jpg",
            "LIBRARY_PC": "library-pcs.jpg",
            "COMPUTER_LAB": "teaching-lab.jpg",
            "STUDY_ROOM": "group-study.jpg",
        }
        area_cards = [
            {"space": space, "count": sum(r.space_id == space.id for r in visible)}
            for space in spaces.values()
            if any(r.space_id == space.id for r in visible)
        ]
        return render_template("resources.html", page_title="Explore resources", resources=visible, statuses=statuses,
                               category=category, term=term, total=len(records),
                               room_count=sum(r.category == "ROOM" for r in records),
                               equipment_count=sum(r.category == "EQUIPMENT" for r in records),
                               spaces=spaces, space_count=len(spaces),
                               area_cards=area_cards, area_images=area_images)

    @app.get("/resources/<int:resource_id>")
    @login_required
    def resource_detail(resource_id: int):
        try:
            resource = service.get_resource(actor_id(), resource_id)
        except BookingError as exc:
            return resolve_error(exc, url_for("resources"))
        spaces = {s.id: s for s in service.list_spaces(actor_id())}
        space = spaces.get(resource.space_id)
        if not resource.is_listed:
            abort(404)
        suggested_start, suggested_end = time_suggestions(space)
        # Preserve the user's chosen time after an availability check or
        # failed booking. Never substitute an unvalidated browser value.
        chosen_start = request.args.get("start", "")
        chosen_end = request.args.get("end", "")
        try:
            datetime.strptime(chosen_start, "%Y-%m-%dT%H:%M")
            datetime.strptime(chosen_end, "%Y-%m-%dT%H:%M")
        except ValueError:
            chosen_start, chosen_end = suggested_start, suggested_end
        statuses = service.status_overview(actor_id())
        return render_template("resource_detail.html", page_title=resource.name,
                               resource=resource, current_status=statuses[resource.id],
                               start=chosen_start, end=chosen_end, space=space)

    def resume_booking_url(resource_id: int) -> str:
        return url_for("resource_detail", resource_id=resource_id,
                       start=request.form.get("start", "")[:16],
                       end=request.form.get("end", "")[:16])

    @app.post("/resources/<int:resource_id>/availability")
    @login_required
    def check_availability(resource_id: int):
        back = resume_booking_url(resource_id)
        try:
            window = form_window()
            result = service.available(actor_id(), resource_id, window)
            flash("This time slot is available. You can submit a request." if result
                  else "This time slot is unavailable. Please choose another time.",
                  "success" if result else "error")
        except BookingError as exc:
            return resolve_error(exc, back)
        return redirect(back)

    @app.post("/resources/<int:resource_id>/book")
    @login_required
    def book(resource_id: int):
        try:
            if g.user.role == "ADMIN":
                abort(403)
            record = service.request(actor_id(), resource_id, form_window())
            flash("Reservation confirmed!" if record.status == "CONFIRMED"
                  else "Request sent! An administrator will review it.", "success")
            return redirect(url_for("my_reservations"))
        except BookingError as exc:
            return resolve_error(exc, resume_booking_url(resource_id))

    @app.get("/my-reservations")
    @login_required
    def my_reservations():
        bookings = service.list_own(actor_id())
        names = {r.id: r for r in service.list_resources(actor_id(), include_hidden=True)}
        return render_template("my_reservations.html", page_title="My reservations", bookings=bookings[::-1],
                               resource_names=names, utc_now=datetime.now(timezone.utc))

    @app.get("/reservations/<int:reservation_id>")
    @login_required
    def reservation_detail(reservation_id: int):
        try:
            booking = service.get_own(actor_id(), reservation_id)
            events = service.events(actor_id(), reservation_id)
            resource = service.get_resource(actor_id(), booking.resource_id)
        except BookingError as exc:
            return resolve_error(exc, url_for("my_reservations"))
        return render_template("reservation_detail.html", page_title=f"Reservation #{booking.id}",
                               booking=booking, events=events, resource=resource,
                               utc_now=datetime.now(timezone.utc))

    @app.post("/reservations/<int:reservation_id>/cancel")
    @login_required
    def cancel_reservation(reservation_id: int):
        try:
            service.cancel(actor_id(), reservation_id)
            flash("Your reservation has been cancelled.", "success")
        except BookingError as exc:
            return resolve_error(exc, url_for("my_reservations"))
        return redirect(url_for("my_reservations"))

    @app.get("/admin")
    @admin_required
    def admin():
        pending = service.list_pending(actor_id())
        resources = service.list_resources(actor_id(), include_hidden=True)
        spaces = service.list_spaces(actor_id())
        return render_template("admin.html", page_title="Administration", pending=pending,
                               resources=resources, spaces=spaces,
                               active_count=sum(r.is_enabled and r.is_listed for r in resources))

    @app.post("/admin/requests/<int:reservation_id>/<choice>")
    @admin_required
    def admin_decision(reservation_id: int, choice: str):
        if choice not in ("approve", "reject"):
            abort(404)
        try:
            service.decide(actor_id(), reservation_id, approve=(choice == "approve"))
            flash("Request approved." if choice == "approve" else "Request rejected.", "success")
        except BookingError as exc:
            return resolve_error(exc, url_for("admin"))
        return redirect(url_for("admin"))

    @app.post("/admin/resources")
    @admin_required
    def admin_create_resource():
        try:
            service.create_resource(actor_id(), request.form.get("code", ""),
                                    request.form.get("name", ""), request.form.get("category", ""),
                                    requires_approval=(request.form.get("requires_approval") == "on"),
                                    space_id=int(request.form["space_id"]) if request.form.get("space_id", "").isdigit() else None)
            flash("Resource added to catalogue.", "success")
        except BookingError as exc:
            return resolve_error(exc, url_for("admin"))
        return redirect(url_for("admin"))

    @app.post("/admin/resources/<int:resource_id>")
    @admin_required
    def admin_edit_resource(resource_id: int):
        try:
            service.update_resource(actor_id(), resource_id, name=request.form.get("name", ""),
                                    category=request.form.get("category", ""),
                                    requires_approval=(request.form.get("requires_approval") == "on"),
                                    is_enabled=(request.form.get("is_enabled") == "on"),
                                    is_listed=(request.form.get("is_listed") == "on") if request.form.get("is_listed_present") == "1" else None,
                                    space_id=int(request.form["space_id"]) if request.form.get("space_id", "").isdigit() else None)
            flash("Resource settings saved.", "success")
        except BookingError as exc:
            return resolve_error(exc, url_for("admin"))
        return redirect(url_for("admin"))

    @app.post("/admin/spaces")
    @admin_required
    def admin_create_space():
        try:
            service.create_space(
                actor_id(),
                request.form.get("code", ""),
                request.form.get("name", ""),
                request.form.get("kind", ""),
                request.form.get("opens_at", ""),
                request.form.get("closes_at", ""),
                request.form.get("open_days", ""),
            )
            flash("Space created.", "success")
        except BookingError as exc:
            return resolve_error(exc, url_for("admin"))
        return redirect(url_for("admin"))

    @app.post("/admin/spaces/<int:space_id>/closures")
    @admin_required
    def admin_add_closure(space_id: int):
        try:
            svc_window = form_window()
            service.create_closure(actor_id(), space_id, svc_window,
                                   request.form.get("reason", ""))
            flash("Teaching/maintenance closure saved.", "success")
        except BookingError as exc:
            return resolve_error(exc, url_for("admin"))
        return redirect(url_for("admin"))

    @app.post("/admin/spaces/<int:space_id>/hours")
    @admin_required
    def admin_change_hours(space_id: int):
        try:
            service.update_space_hours(actor_id(), space_id,
                                       request.form.get("opens_at", ""),
                                       request.form.get("closes_at", ""),
                                       request.form.get("open_days", ""))
            flash("Opening hours updated.", "success")
        except BookingError as exc:
            return resolve_error(exc, url_for("admin"))
        return redirect(url_for("admin"))

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    def error_page(exc):
        return render_template("error.html", page_title=str(exc.code), error_code=exc.code,
                               error_description=getattr(exc, "description", "Request failed")), exc.code

    return app
