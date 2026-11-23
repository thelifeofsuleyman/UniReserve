"""Trusted account provisioning and salted password hashes."""
from __future__ import annotations
import hashlib
import hmac
import os
from sqlalchemy import select
from sqlalchemy.engine import Engine
from unireserve.storage.db import write_transaction
from unireserve.storage.models import User

ITERATIONS = 310_000

def hash_password(password: str) -> str:
    if not isinstance(password, str) or len(password) < 10:
        raise ValueError("passwords must have at least 10 characters")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return "pbkdf2_sha256$%s$%s$%s" % (ITERATIONS, salt.hex(), digest.hex())

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, work, salt_hex, digest_hex = encoded.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        count = int(work)
        if count < 100_000 or count > 2_000_000:
            return False
        salt = bytes.fromhex(salt_hex)
        digest = bytes.fromhex(digest_hex)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, count)
        return hmac.compare_digest(candidate, digest)
    except (ValueError, AttributeError, TypeError):
        return False

def provision_user(engine: Engine, email: str, password: str, role: str) -> int:
    """Trusted one-off setup tool, not an unauthenticated web route."""
    email = email.strip().casefold()
    if not email or "@" not in email or role not in ("STUDENT", "STAFF", "ADMIN"):
        raise ValueError("valid email and role required")
    password_hash = hash_password(password)
    with write_transaction(engine) as session:
        if session.scalar(select(User.id).where(User.email == email)) is not None:
            raise ValueError("email already exists")
        user = User(email=email, password_hash=password_hash, role=role, is_active=True)
        session.add(user)
        session.flush()
        return user.id

# Backward-compatible alias used by existing test fixtures and sample setup.
provision_demo_user = provision_user
