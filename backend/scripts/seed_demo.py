"""Seed the dev SQLite DB with demo users + listings for manual testing.

Run from the backend/ directory:

    uv run python scripts/seed_demo.py

Idempotent: existing users (matched by email) and listings (matched by
host+title) are left untouched. Re-running only fills in what's missing.

All demo users share the same password so you can log in as any of them
to exercise messaging between accounts:

    Password: Password123!
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Make `app` importable when running this file directly.
SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

from app.core.auth import hash_password  # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.college import College 
from app.models.listing import Listing  # noqa: E402
from app.models.profiles import Profile  # noqa: E402
from app.models.user import User  # noqa: E402

DEMO_PASSWORD = "Password123!"

# SDSU is roughly (32.7757, -117.0719). Listings are clustered nearby.
DEMO_USERS = [
    {
        "email": "alice.demo@example.com",
        "username": "alicedemo",
        "firstname": "Alice",
        "lastname": "Nguyen",
        "description": "CS junior at SDSU. Subletting my place for the summer.",
    },
    {
        "email": "bob.demo@example.com",
        "username": "bobdemo",
        "firstname": "Bob",
        "lastname": "Garcia",
        "description": "Mech-E senior. Looking to pass on my lease.",
    },
    {
        "email": "carla.demo@example.com",
        "username": "carlademo",
        "firstname": "Carla",
        "lastname": "Patel",
        "description": "Studying abroad next semester.",
    },
    {
        "email": "diego.demo@example.com",
        "username": "diegodemo",
        "firstname": "Diego",
        "lastname": "Martinez",
        "description": "Grad student in CompE.",
    },
    {
        "email": "emma.demo@example.com",
        "username": "emmademo",
        "firstname": "Emma",
        "lastname": "Wright",
        "description": "Graduating in May, lease ends in August.",
    },
    {
        "email": "frank.demo@example.com",
        "username": "frankdemo",
        "firstname": "Frank",
        "lastname": "Lopez",
        "description": "Roommate moved out, room available.",
    },
]

# 2 listings per demo user.
DEMO_LISTINGS: list[dict] = [
    # Alice
    {
        "owner": "alicedemo",
        "title": "Sunny 1BR near SDSU trolley",
        "description": "One bedroom in a quiet 4-unit building. 5 min walk to the trolley, fully furnished, in-unit laundry.",
        "price": 1450.0,
        "location": "5500 Hardy Ave, San Diego, CA",
        "room_type": "single",
        "sqft": 520,
        "latitude": 32.7762,
        "longitude": -117.0712,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1200",
            "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1200",
        ],
    },
    {
        "owner": "alicedemo",
        "title": "Shared room in 3BR house",
        "description": "Spot in a shared bedroom with one other roommate. Backyard, parking, walking distance to campus.",
        "price": 850.0,
        "location": "5800 Montezuma Rd, San Diego, CA",
        "room_type": "shared",
        "sqft": 220,
        "latitude": 32.7711,
        "longitude": -117.0679,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=1200",
        ],
    },
    # Bob
    {
        "owner": "bobdemo",
        "title": "Modern studio with pool access",
        "description": "Bright studio in a complex with rooftop pool and gym. Lease takeover June through August.",
        "price": 1700.0,
        "location": "6303 Friars Rd, San Diego, CA",
        "room_type": "studio",
        "sqft": 410,
        "latitude": 32.7710,
        "longitude": -117.1535,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1200",
            "https://images.unsplash.com/photo-1494203484021-3c454daf695d?w=1200",
        ],
    },
    {
        "owner": "bobdemo",
        "title": "Private room in 2BR — College Area",
        "description": "Master bedroom with private bath. Cat-friendly, washer/dryer in unit.",
        "price": 1250.0,
        "location": "5200 College Ave, San Diego, CA",
        "room_type": "single",
        "sqft": 320,
        "latitude": 32.7705,
        "longitude": -117.0660,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200",
        ],
    },
    # Carla
    {
        "owner": "carlademo",
        "title": "Cozy 2BR — fall semester sublet",
        "description": "Looking to sublet entire 2BR while I'm abroad. Furnished, utilities included.",
        "price": 2200.0,
        "location": "4800 Art St, San Diego, CA",
        "room_type": "double",
        "sqft": 780,
        "latitude": 32.7649,
        "longitude": -117.0727,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1486304873000-235643847519?w=1200",
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200",
        ],
    },
    {
        "owner": "carlademo",
        "title": "Quiet single room near library",
        "description": "Single in a 4BR with grad students. Quiet, no parties.",
        "price": 950.0,
        "location": "6100 Aztec Cir Dr, San Diego, CA",
        "room_type": "single",
        "sqft": 180,
        "latitude": 32.7753,
        "longitude": -117.0696,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=1200",
        ],
    },
    # Diego
    {
        "owner": "diegodemo",
        "title": "Loft-style 1BR in North Park",
        "description": "Industrial loft, exposed brick, 15 min drive to campus. Great for a grad student.",
        "price": 1900.0,
        "location": "3000 Upas St, San Diego, CA",
        "room_type": "single",
        "sqft": 600,
        "latitude": 32.7479,
        "longitude": -117.1297,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=1200",
        ],
    },
    {
        "owner": "diegodemo",
        "title": "Room in 3BR townhome — June start",
        "description": "Private bedroom, shared bath, modern townhome with garage parking.",
        "price": 1100.0,
        "location": "5500 Adobe Falls Rd, San Diego, CA",
        "room_type": "single",
        "sqft": 240,
        "latitude": 32.7795,
        "longitude": -117.0566,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=1200",
        ],
    },
    # Emma
    {
        "owner": "emmademo",
        "title": "Lease takeover — graduating senior",
        "description": "Full 1BR apartment, lease through August. Pet-friendly building.",
        "price": 1550.0,
        "location": "5050 Canyon Crest Dr, San Diego, CA",
        "room_type": "single",
        "sqft": 540,
        "latitude": 32.7689,
        "longitude": -117.0742,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1502673530728-f79b4cab31b1?w=1200",
            "https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=1200",
        ],
    },
    {
        "owner": "emmademo",
        "title": "Sublet — large room with balcony",
        "description": "Big bedroom with private balcony, partially furnished. Female roommates only please.",
        "price": 1050.0,
        "location": "5400 55th St, San Diego, CA",
        "room_type": "single",
        "sqft": 280,
        "latitude": 32.7741,
        "longitude": -117.0608,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200",
        ],
    },
    # Frank
    {
        "owner": "frankdemo",
        "title": "Open spot in 4BR house",
        "description": "Roommate just moved out — last-minute opening. Backyard, BBQ, two friendly cats.",
        "price": 900.0,
        "location": "5650 Aragon Dr, San Diego, CA",
        "room_type": "single",
        "sqft": 200,
        "latitude": 32.7612,
        "longitude": -117.0577,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1200",
        ],
    },
    {
        "owner": "frankdemo",
        "title": "Studio steps from campus",
        "description": "Tiny but mighty studio, 2-min walk to SDSU. Available immediately.",
        "price": 1350.0,
        "location": "6000 Montezuma Rd, San Diego, CA",
        "room_type": "studio",
        "sqft": 320,
        "latitude": 32.7727,
        "longitude": -117.0702,
        "college_id": 26,
        "image_urls": [
            "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=1200",
        ],
    },
]


def upsert_users(db) -> dict[str, User]:
    """Create demo users (and their profiles) if they don't already exist."""
    by_username: dict[str, User] = {}
    pwd = hash_password(DEMO_PASSWORD)

    for spec in DEMO_USERS:
        existing = db.query(User).filter(User.email == spec["email"]).first()
        if existing:
            by_username[spec["username"]] = existing
            print(f"  · user exists: {spec['username']} (id={existing.id})")
            continue

        user = User(
            email=spec["email"],
            username=spec["username"],
            password_hash=pwd,
        )
        db.add(user)
        db.flush()  # populate user.id

        profile = Profile(
            user_id=user.id,
            firstname=spec["firstname"],
            lastname=spec["lastname"],
            username=spec["username"],
            description=spec["description"],
        )
        db.add(profile)

        by_username[spec["username"]] = user
        print(f"  + created user: {spec['username']} (id={user.id})")

    db.commit()
    return by_username


def upsert_listings(db, users_by_username: dict[str, User]) -> int:
    """Create demo listings if (host, title) combo doesn't already exist."""
    now = datetime.now(UTC)
    created = 0

    for i, spec in enumerate(DEMO_LISTINGS):
        owner = users_by_username[spec["owner"]]

        already = (
            db.query(Listing)
            .filter(Listing.host_id == owner.id, Listing.title == spec["title"])
            .first()
        )
        if already:
            print(f"  · listing exists: {spec['title']!r}")
            continue

        # Stagger start dates so listings don't all look identical.
        start = now + timedelta(days=14 + i * 3)
        end = start + timedelta(days=120)

        urls = spec["image_urls"]
        listing = Listing(
            host_id=owner.id,
            title=spec["title"],
            description=spec["description"],
            price=spec["price"],
            location=spec["location"],
            room_type=spec["room_type"],
            sqft=spec["sqft"],
            start_date=start,
            end_date=end,
            college_id=26,
            thumbnail_url=urls[0],
            image_urls=urls,
            latitude=spec["latitude"],
            longitude=spec["longitude"],
        )
        db.add(listing)
        created += 1
        print(f"  + created listing: {spec['title']!r} (host={owner.username})")

    db.commit()
    return created

def main() -> None:
    Base.metadata.create_all(bind=engine)  # safety net if DB is fresh
    db = SessionLocal()
    try:
        print("Seeding users…")
        users = upsert_users(db)
        print(f"\nSeeding listings…")
        new_listings = upsert_listings(db, users)

        print("\nDone.")
        print(f"  users seeded: {len(users)}")
        print(f"  listings created this run: {new_listings}")
        print(f"\nLog in with any of these emails / password '{DEMO_PASSWORD}':")
        for spec in DEMO_USERS:
            print(f"  · {spec['email']}  ({spec['username']})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
