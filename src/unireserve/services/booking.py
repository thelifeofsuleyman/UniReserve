"""Booking service implementing FR-003–FR-011 and ADR-0002.

Every state-changing operation loads roles from the database and runs inside
an immediate SQLite write transaction. This is service code, not an HTTP API.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from unireserve.domain.availability import TimeWindow
from unireserve.domain.live_status import ConfirmedInterval, StatusView, current_status
from unireserve.storage.db import write_transaction
from unireserve.storage.models import Reservation, ReservationEvent, Resource, User


class BookingError(Exception):
    """Known, user-safe business-rule failure."""


class AccessDenied(BookingError):
    pass


class InvalidRequest(BookingError):
    pass


class Conflict(BookingError):
    pass


class MissingRecord(BookingError):
    pass


@dataclass(frozen=True)
class BookingRecord:
    id: int
    user_id: int
    resource_id: int
    start_utc: datetime
    end_utc: datetime
    status: str


@dataclass(frozen=True)
class ResourceRecord:
    id: int
    public_code: str
    name: str
    category: str
    requires_approval: bool
    is_enabled: bool




@dataclass(frozen=True)
class PendingRequestRecord:
    """Approval inbox display record, visible exclusively to administrators."""
    id: int
    user_email: str
    resource_name: str
    resource_code: str
    start_utc: datetime
    end_utc: datetime
    status: str


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidRequest("a timezone-aware datetime is required")
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _from_naive_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc)


def _view(booking: Reservation) -> BookingRecord:
    return BookingRecord(
        id=booking.id, user_id=booking.user_id, resource_id=booking.resource_id,
        start_utc=_from_naive_utc(booking.start_utc),
        end_utc=_from_naive_utc(booking.end_utc), status=booking.status,
    )


def _resource_view(resource: Resource) -> ResourceRecord:
    return ResourceRecord(
        resource.id, resource.public_code, resource.name, resource.category,
        resource.requires_approval, resource.is_enabled,
    )


class BookingService:
    def __init__(self, engine: Engine, clock: Callable[[], datetime] = _utc_now):
        self.engine = engine
        self.clock = clock

    def _now(self, now: datetime | None) -> datetime:
        return _to_naive_utc(now if now is not None else self.clock())

    @staticmethod
    def _actor(session: Session, actor_id: int, *, admin: bool = False) -> User:
        user = session.get(User, actor_id)
        if user is None or not user.is_active:
            raise AccessDenied("authentication is required")
        if admin and user.role != "ADMIN":
            raise AccessDenied("administrator access required")
        return user

    @staticmethod
    def _resource(session: Session, resource_id: int) -> Resource:
        resource = session.get(Resource, resource_id)
        if resource is None:
            raise MissingRecord("resource not found")
        return resource

    @staticmethod
    def _no_conflict(session: Session, resource_id: int, start: datetime, end: datetime) -> bool:
        existing = session.scalar(
            select(Reservation.id).where(
                Reservation.resource_id == resource_id,
                Reservation.status == "CONFIRMED",
                Reservation.start_utc < end,
                Reservation.end_utc > start,
            ).limit(1)
        )
        return existing is None

    @staticmethod
    def _request_valid(window: TimeWindow, resource: Resource, now: datetime) -> tuple[datetime, datetime]:
        start = _to_naive_utc(window.start)
        end = _to_naive_utc(window.end)
        if start <= now:
            raise InvalidRequest("reservation must start in the future")
        if start > now + timedelta(days=14):
            raise InvalidRequest("reservation start exceeds the 14-day horizon")
        limit = timedelta(hours=2 if resource.category == "ROOM" else 24)
        if end - start > limit:
            raise InvalidRequest("reservation exceeds category duration limit")
        return start, end

    @staticmethod
    def _event(session: Session, booking: Reservation, actor_id: int, action: str,
               previous: str | None, new: str, now: datetime) -> None:
        session.add(ReservationEvent(
            reservation_id=booking.id, actor_user_id=actor_id,
            action=action, previous_status=previous, new_status=new, occurred_utc=now,
        ))

    def list_resources(self, actor_id: int) -> list[ResourceRecord]:
        with Session(self.engine) as session:
            self._actor(session, actor_id)
            return [_resource_view(r) for r in session.scalars(select(Resource).order_by(Resource.id)).all()]


    def get_resource(self, actor_id: int, resource_id: int) -> ResourceRecord:
        """Inspect a resource; identity is verified against current DB account."""
        with Session(self.engine) as session:
            self._actor(session, actor_id)
            return _resource_view(self._resource(session, resource_id))

    def list_pending(self, actor_id: int) -> list[PendingRequestRecord]:
        """Administrator-only approval queue; requesters' emails are not public."""
        with Session(self.engine) as session:
            self._actor(session, actor_id, admin=True)
            rows = session.execute(
                select(Reservation, User.email, Resource.name, Resource.public_code)
                .join(User, Reservation.user_id == User.id)
                .join(Resource, Reservation.resource_id == Resource.id)
                .where(Reservation.status == "PENDING_APPROVAL")
                .order_by(Reservation.created_utc, Reservation.id)
            ).all()
            return [PendingRequestRecord(b.id, email, name, code,
                                         _from_naive_utc(b.start_utc), _from_naive_utc(b.end_utc),
                                         b.status)
                    for b, email, name, code in rows]

    def status_overview(self, actor_id: int, *, now: datetime | None = None) -> dict[int, StatusView]:
        """Authenticated read-only availability snapshot for visual UI.

        No requester identities or private reservation details are exposed.
        The 15-minute state is about the *next confirmed* booking only.
        """
        moment = self._now(now)
        aware_now = _from_naive_utc(moment)
        with Session(self.engine) as session:
            self._actor(session, actor_id)
            resources = session.scalars(select(Resource).order_by(Resource.id)).all()
            active_or_future = session.scalars(
                select(Reservation).where(
                    Reservation.status == "CONFIRMED", Reservation.end_utc > moment
                ).order_by(Reservation.start_utc)
            ).all()
            grouped: dict[int, list[ConfirmedInterval]] = {r.id: [] for r in resources}
            for booking in active_or_future:
                grouped.setdefault(booking.resource_id, []).append(ConfirmedInterval(
                    _from_naive_utc(booking.start_utc), _from_naive_utc(booking.end_utc)))
            return {r.id: current_status(r.is_enabled, grouped[r.id], aware_now)
                    for r in resources}

    def available(self, actor_id: int, resource_id: int, window: TimeWindow) -> bool:
        with Session(self.engine) as session:
            self._actor(session, actor_id)
            resource = self._resource(session, resource_id)
            self._request_valid(window, resource, self._now(None))
            return resource.is_enabled and self._no_conflict(
                session, resource_id, _to_naive_utc(window.start), _to_naive_utc(window.end)
            )

    def request(self, actor_id: int, resource_id: int, window: TimeWindow,
                *, now: datetime | None = None) -> BookingRecord:
        moment = self._now(now)
        with write_transaction(self.engine) as session:
            actor = self._actor(session, actor_id)
            if actor.role not in ("STUDENT", "STAFF"):
                raise AccessDenied("only students and staff may request bookings")
            resource = self._resource(session, resource_id)
            if not resource.is_enabled:
                raise InvalidRequest("resource is disabled")
            start, end = self._request_valid(window, resource, moment)
            # Pending requests do not reserve capacity, but requests for an
            # already confirmed slot are rejected even for restricted resources.
            if not self._no_conflict(session, resource_id, start, end):
                raise Conflict("resource is already reserved for this interval")
            status = "PENDING_APPROVAL" if resource.requires_approval else "CONFIRMED"
            booking = Reservation(user_id=actor.id, resource_id=resource.id,
                                  start_utc=start, end_utc=end, status=status, created_utc=moment)
            session.add(booking)
            session.flush()  # event must reference persisted booking ID
            self._event(session, booking, actor.id, "CREATED", None, status, moment)
            return _view(booking)

    def list_own(self, actor_id: int) -> list[BookingRecord]:
        with Session(self.engine) as session:
            self._actor(session, actor_id)
            rows = session.scalars(
                select(Reservation).where(Reservation.user_id == actor_id).order_by(Reservation.id)
            ).all()
            return [_view(row) for row in rows]

    def get_own(self, actor_id: int, reservation_id: int) -> BookingRecord:
        with Session(self.engine) as session:
            self._actor(session, actor_id)
            row = session.scalar(select(Reservation).where(
                Reservation.id == reservation_id, Reservation.user_id == actor_id
            ))
            if row is None:
                raise MissingRecord("reservation not found")
            return _view(row)

    def cancel(self, actor_id: int, reservation_id: int,
               *, now: datetime | None = None) -> BookingRecord:
        moment = self._now(now)
        with write_transaction(self.engine) as session:
            self._actor(session, actor_id)
            booking = session.get(Reservation, reservation_id)
            if booking is None or booking.user_id != actor_id:
                raise MissingRecord("reservation not found")
            if booking.status not in ("PENDING_APPROVAL", "CONFIRMED"):
                raise InvalidRequest("this reservation cannot be cancelled")
            if moment >= booking.start_utc:
                raise InvalidRequest("cancellation cutoff has passed")
            previous = booking.status
            booking.status = "CANCELLED"
            self._event(session, booking, actor_id, "CANCELLED", previous, booking.status, moment)
            return _view(booking)

    def decide(self, actor_id: int, reservation_id: int, *, approve: bool,
               now: datetime | None = None) -> BookingRecord:
        moment = self._now(now)
        with write_transaction(self.engine) as session:
            self._actor(session, actor_id, admin=True)
            booking = session.get(Reservation, reservation_id)
            if booking is None:
                raise MissingRecord("reservation not found")
            if booking.status != "PENDING_APPROVAL":
                raise InvalidRequest("request is no longer pending")
            if approve:
                resource = self._resource(session, booking.resource_id)
                if not resource.is_enabled:
                    raise InvalidRequest("resource is disabled")
                if booking.start_utc <= moment:
                    raise InvalidRequest("cannot approve a reservation that has already started")
                if not self._no_conflict(session, booking.resource_id, booking.start_utc, booking.end_utc):
                    raise Conflict("another confirmed booking occupies the interval")
            booking.status = "CONFIRMED" if approve else "REJECTED"
            self._event(session, booking, actor_id, "APPROVED" if approve else "REJECTED",
                        "PENDING_APPROVAL", booking.status, moment)
            return _view(booking)

    def create_resource(self, actor_id: int, code: str, name: str, category: str,
                        *, requires_approval: bool = False) -> ResourceRecord:
        if not code.strip() or not name.strip() or category not in ("ROOM", "EQUIPMENT"):
            raise InvalidRequest("valid code, name and category are required")
        with write_transaction(self.engine) as session:
            self._actor(session, actor_id, admin=True)
            if session.scalar(select(Resource.id).where(Resource.public_code == code.strip())) is not None:
                raise InvalidRequest("resource code already exists")
            resource = Resource(public_code=code.strip(), name=name.strip(), category=category,
                                requires_approval=requires_approval, is_enabled=True)
            session.add(resource)
            session.flush()
            return _resource_view(resource)

    def update_resource(self, actor_id: int, resource_id: int, *, name: str | None = None,
                        category: str | None = None, requires_approval: bool | None = None,
                        is_enabled: bool | None = None) -> ResourceRecord:
        if name is not None and not name.strip():
            raise InvalidRequest("resource name is required")
        if category is not None and category not in ("ROOM", "EQUIPMENT"):
            raise InvalidRequest("unsupported resource category")
        with write_transaction(self.engine) as session:
            self._actor(session, actor_id, admin=True)
            resource = self._resource(session, resource_id)
            if name is not None:
                resource.name = name.strip()
            if category is not None:
                resource.category = category
            if requires_approval is not None:
                resource.requires_approval = requires_approval
            if is_enabled is not None:
                resource.is_enabled = is_enabled
            session.flush()
            return _resource_view(resource)

    def events(self, actor_id: int, reservation_id: int) -> list[tuple[str, str | None, str]]:
        """View the audit trail, visible only to owner or administrator."""
        with Session(self.engine) as session:
            actor = self._actor(session, actor_id)
            booking = session.get(Reservation, reservation_id)
            if booking is None or (actor.role != "ADMIN" and booking.user_id != actor_id):
                raise MissingRecord("reservation not found")
            rows = session.scalars(select(ReservationEvent).where(
                ReservationEvent.reservation_id == reservation_id
            ).order_by(ReservationEvent.id)).all()
            return [(e.action, e.previous_status, e.new_status) for e in rows]
