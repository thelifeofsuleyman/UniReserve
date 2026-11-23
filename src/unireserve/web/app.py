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

from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)
from sqlalchemy.orm import Session
from sqlalchemy import select

from unireserve.domain.availability import TimeWindow
from unireserve.services.booking import (
    AccessDenied, BookingService, Conflict, InvalidRequest, MissingRecord, BookingError,
)
from unireserve.storage.accounts import verify_password
from unireserve.storage.db import create_schema, make_engine
from unireserve.storage.models import User


BASE_DIR = Path(__file__).resolve().parents[3]


def create_app(test_config: dict | None = None) -> Flask:
    """Create an isolated Flask application (supports test database injection)."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(
        SECRET_KEY=os.environ.get("UNIRESERVE_SECRET_KEY") or secrets.token_hex(32),
        DB_PATH=os.environ.get("UNIRESERVE_DB_PATH") or str(BASE_DIR / "instance" / "unireserve.sqlite3"),
        DISPLAY_TIMEZONE=os.environ.get("UNIRESERVE_TIMEZONE", "Asia/Baku"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # local http://127.0.0.1 demonstration only
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config is not None:
        app.config.update(test_config)
    try:
        display_zone = ZoneInfo(app.config["DISPLAY_TIMEZONE"])
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError("Invalid UNIRESERVE_TIMEZONE; install tzdata if required") from exc
    engine = make_engine(app.config["DB_PATH"])
    create_schema(engine)
    service = BookingService(engine)
    app.extensions["unireserve_engine"] = engine

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

    def time_suggestions():
        local_now = datetime.now(display_zone)
        start = (local_now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        # Always at least 1h in the future.
        if start <= local_now:
            start += timedelta(hours=1)
        end = start + timedelta(hours=1)
        return start.strftime("%Y-%m-%dT%H:%M"), end.strftime("%Y-%m-%dT%H:%M")

    @app.get("/")
    def index():
        return redirect(url_for("resources") if g.user else url_for("login"))

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

    @app.get("/resources")
    @login_required
    def resources():
        records = service.list_resources(actor_id())
        category = request.args.get("category", "ALL").upper()
        if category not in ("ALL", "ROOM", "EQUIPMENT"):
            category = "ALL"
        term = request.args.get("q", "").strip()[:100]
        visible = [r for r in records if (category == "ALL" or r.category == category)
                   and (not term or term.casefold() in (r.name + " " + r.public_code).casefold())]
        return render_template("resources.html", page_title="Explore resources", resources=visible,
                               category=category, term=term, total=len(records),
                               room_count=sum(r.category == "ROOM" for r in records),
                               equipment_count=sum(r.category == "EQUIPMENT" for r in records))

    @app.get("/resources/<int:resource_id>")
    @login_required
    def resource_detail(resource_id: int):
        try:
            resource = service.get_resource(actor_id(), resource_id)
        except BookingError as exc:
            return resolve_error(exc, url_for("resources"))
        suggested_start, suggested_end = time_suggestions()
        return render_template("resource_detail.html", page_title=resource.name,
                               resource=resource, start=suggested_start, end=suggested_end)

    @app.post("/resources/<int:resource_id>/availability")
    @login_required
    def check_availability(resource_id: int):
        try:
            window = form_window()
            result = service.available(actor_id(), resource_id, window)
            flash("This time slot is available. You can submit a request." if result
                  else "This time slot is unavailable. Please choose another time.",
                  "success" if result else "error")
        except BookingError as exc:
            return resolve_error(exc, url_for("resource_detail", resource_id=resource_id))
        return redirect(url_for("resource_detail", resource_id=resource_id))

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
            return resolve_error(exc, url_for("resource_detail", resource_id=resource_id))

    @app.get("/my-reservations")
    @login_required
    def my_reservations():
        bookings = service.list_own(actor_id())
        names = {r.id: r for r in service.list_resources(actor_id())}
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
        resources = service.list_resources(actor_id())
        return render_template("admin.html", page_title="Administration", pending=pending,
                               resources=resources, active_count=sum(r.is_enabled for r in resources))

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
                                    requires_approval=(request.form.get("requires_approval") == "on"))
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
                                    is_enabled=(request.form.get("is_enabled") == "on"))
            flash("Resource settings saved.", "success")
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
