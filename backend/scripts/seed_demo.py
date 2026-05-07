"""Seed the dev SQLite DB with demo users + listings for manual testing.

Run from the backend/ directory:

    uv run python scripts/seed_demo.py

Idempotent: existing users (matched by email) and listings (matched by
host+title) are left untouched. Re-running only fills in what's missing.

All demo users share the same password so you can log in as any of them
to exercise messaging between accounts:

    Password: Password123!

Produces 36 demo users and 112 listings (12 hand-crafted + 100 generated).
The generated listings use a fixed RNG seed so the dataset is stable across
runs.
"""

from __future__ import annotations

import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Make `app` importable when running this file directly.
SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

from app.core.auth import hash_password  # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.college import College  # noqa: E402, F401
from app.models.listing import Listing  # noqa: E402
from app.models.profiles import Profile  # noqa: E402
from app.models.user import User  # noqa: E402

DEMO_PASSWORD = "Password123!"
SDSU_COLLEGE_ID = 26
GENERATED_COUNT = 100
RNG_SEED = 42

# ---------------------------------------------------------------------------
# Hand-crafted demo users (kept stable for existing manual-test logins).
# ---------------------------------------------------------------------------

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

# 2 listings per hand-crafted user.
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
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
        "college_id": SDSU_COLLEGE_ID,
        "image_urls": [
            "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=1200",
        ],
    },
]

# ---------------------------------------------------------------------------
# Extra demo users — give us enough hosts to spread 100 listings across.
# ---------------------------------------------------------------------------

_EXTRA_USER_SPECS: list[tuple[str, str, str]] = [
    ("Sophia",  "Rivera",    "Nursing major, softball team."),
    ("Liam",    "Chen",      "Physics PhD student. Spends most nights in the lab."),
    ("Olivia",  "Brooks",    "Art history senior, will swap for plant care."),
    ("Noah",    "Harper",    "Civil engineering, big dog person."),
    ("Maya",    "Singh",     "Pre-med junior. Quiet, clean roommate."),
    ("Ethan",   "Park",      "EE senior, builds keyboards in his spare time."),
    ("Isabella","Torres",    "Communications major, RA last year."),
    ("Jacob",   "Wallace",   "Aerospace student, half the year I'm at internships."),
    ("Ava",     "Mitchell",  "Marketing junior, weekend yoga teacher."),
    ("Mason",   "Khan",      "MIS major, gym-goer, no parties."),
    ("Charlotte","Bennett",  "English lit grad student. Coffee snob."),
    ("Lucas",   "Romero",    "Business major, on the surf team."),
    ("Harper",  "Davis",     "Public health student, vegetarian kitchen."),
    ("Daniel",  "Kim",       "CS sophomore, prefers nightly study sessions."),
    ("Amelia",  "Nguyen",    "Bio major, fish tank owner."),
    ("Henry",   "Stewart",   "Finance senior, early-morning runner."),
    ("Mia",     "Foster",    "Psych major, two well-behaved cats."),
    ("Julian",  "Reyes",     "Architecture grad student, always at studio."),
    ("Zoe",     "Sanders",   "Journalism major, freelance photographer."),
    ("Owen",    "Murphy",    "Mech-E junior, weekend hiker."),
    ("Layla",   "Aziz",      "International business, fluent in three languages."),
    ("Caleb",   "Brooks",    "Math major, big into board games."),
    ("Aria",    "Thompson",  "Sustainability major, composts everything."),
    ("Logan",   "Phillips",  "Film major, has soft camera-club lighting."),
    ("Chloe",   "Wong",      "Linguistics senior, host quiet study groups."),
    ("Eli",     "Hernandez", "Kinesiology major, on the club soccer team."),
    ("Aaliyah", "Jones",     "Nursing senior. Looking for chill roommates."),
    ("Ryan",    "ONeill",    "Econ major, runs a campus tutoring side gig."),
    ("Nora",    "Fischer",   "Environmental science, plant lover."),
    ("Dylan",   "Ross",      "Music major, soundproofed practice corner."),
]


def _build_extra_users() -> list[dict]:
    out: list[dict] = []
    for first, last, desc in _EXTRA_USER_SPECS:
        username = (first + last).lower().replace("'", "")
        email = f"{username}.demo@example.com"
        out.append(
            {
                "email": email,
                "username": username,
                "firstname": first,
                "lastname": last,
                "description": desc,
            }
        )
    return out


EXTRA_USERS: list[dict] = _build_extra_users()
ALL_DEMO_USERS: list[dict] = DEMO_USERS + EXTRA_USERS

# ---------------------------------------------------------------------------
# Listing generator — produces deterministic, realistic-looking sublets.
# ---------------------------------------------------------------------------

# (street_name, base_lat, base_lng, neighborhood)
_NEIGHBORHOODS: list[tuple[str, float, float, str]] = [
    ("Montezuma Rd",     32.7711, -117.0679, "College Area"),
    ("College Ave",      32.7705, -117.0660, "College Area"),
    ("El Cajon Blvd",    32.7619, -117.0813, "College Area"),
    ("Hardy Ave",        32.7762, -117.0712, "College Area"),
    ("55th St",          32.7741, -117.0608, "College Area"),
    ("Aztec Cir Dr",     32.7753, -117.0696, "Campus"),
    ("Adobe Falls Rd",   32.7795, -117.0566, "Del Cerro"),
    ("Aragon Dr",        32.7612, -117.0577, "College Area"),
    ("Art St",           32.7649, -117.0727, "Rolando"),
    ("Canyon Crest Dr",  32.7689, -117.0742, "Campus"),
    ("Friars Rd",        32.7710, -117.1535, "Mission Valley"),
    ("Upas St",          32.7479, -117.1297, "North Park"),
    ("Texas St",         32.7563, -117.1276, "North Park"),
    ("University Ave",   32.7479, -117.1326, "Hillcrest"),
    ("La Mesa Blvd",     32.7681, -117.0231, "La Mesa"),
    ("Lake Murray Blvd", 32.7857, -117.0334, "Del Cerro"),
    ("Waring Rd",        32.7878, -117.0531, "Allied Gardens"),
    ("Mission Center Rd",32.7748, -117.1430, "Mission Valley"),
    ("Camino del Rio S", 32.7732, -117.1467, "Mission Valley"),
    ("Linda Vista Rd",   32.7806, -117.1832, "Linda Vista"),
    ("Park Blvd",        32.7466, -117.1437, "University Heights"),
    ("Adams Ave",        32.7654, -117.1256, "Normal Heights"),
]

_ROOM_TYPES = ["single", "shared", "studio", "double"]
_ROOM_TYPE_WEIGHTS = [0.55, 0.13, 0.14, 0.18]

_PRICE_RANGES = {
    "single": (900, 1700),
    "shared": (650, 1100),
    "studio": (1100, 1850),
    "double": (1600, 2700),
}
_SQFT_RANGES = {
    "single": (200, 550),
    "shared": (150, 280),
    "studio": (280, 500),
    "double": (600, 950),
}

_ROOM_PHRASES = {
    "single": ["1BR apartment", "private bedroom", "single room", "1BR unit"],
    "shared": ["shared room", "shared bedroom", "spot in shared room"],
    "studio": ["studio", "studio apartment", "loft studio"],
    "double": ["2BR apartment", "2BR unit", "2-bed sublet"],
}

_DESCRIPTORS = [
    "Sunny", "Quiet", "Cozy", "Modern", "Bright", "Renovated",
    "Spacious", "Charming", "Clean", "Furnished", "Updated", "Airy",
]

_AMENITIES = [
    "in-unit laundry", "private bath", "garage parking", "AC",
    "balcony", "pool access", "gym access", "dishwasher",
    "patio", "rooftop deck", "fenced yard", "fast wifi included",
]

_TERMS = [
    "summer", "fall semester", "spring semester",
    "June start", "August move-in", "lease takeover",
    "12-month lease", "short-term sublet",
]

_TITLE_TEMPLATES = [
    "{descriptor} {phrase} near SDSU",
    "{descriptor} {phrase} — {neighborhood}",
    "{phrase} in {neighborhood}",
    "Sublet: {descriptor} {phrase} — {term}",
    "{descriptor} {phrase} on {street}",
    "{neighborhood} {phrase} — {term}",
    "{phrase} with {amenity}",
]

_DESCRIPTION_TEMPLATES = [
    "{descriptor} {phrase} in {neighborhood}, about {minutes} minutes from SDSU. Comes with {amenity1} and {amenity2}. Available {term}.",
    "{minutes}-minute drive to campus. {phrase_cap} with {amenity1}, {amenity2}, and {amenity3}. Great fit for {audience}.",
    "Looking to sublet a {phrase} in {neighborhood}. Walking distance to {nearby}. Includes {amenity1} and {amenity2}. {term_sentence}.",
    "Available {term}: {phrase} just off {street}. {amenity1_cap}, {amenity2}, and quiet building. {audience_sentence}.",
    "{phrase_cap} in a {descriptor_lower} {neighborhood} unit. {minutes} min from SDSU, with {amenity1} and {amenity2}.",
]

_AUDIENCES = [
    "grad students", "quiet roommates", "a clean roommate", "anyone who likes a calm space",
    "students who study late", "anyone with a tight budget", "early risers",
]

_NEARBY = [
    "the trolley", "the rec center", "Aztec Market", "the campus library",
    "Lake Murray", "Trader Joe's", "Mission Valley mall", "Balboa Park",
]


def _placeholder_images(rng: random.Random, idx: int) -> list[str]:
    n = rng.choice([1, 2, 2, 3])  # weight toward 2 photos
    return [
        f"https://picsum.photos/seed/sublease-{idx}-{k}/1200/800"
        for k in range(n)
    ]


def _generate_listings(
    user_pool: list[str],
    count: int,
    seed: int,
    forbidden_titles: set[str],
) -> list[dict]:
    rng = random.Random(seed)
    out: list[dict] = []
    used_titles: set[str] = set(forbidden_titles)

    for i in range(count):
        owner = user_pool[i % len(user_pool)]
        room_type = rng.choices(_ROOM_TYPES, weights=_ROOM_TYPE_WEIGHTS, k=1)[0]
        phrase = rng.choice(_ROOM_PHRASES[room_type])
        descriptor = rng.choice(_DESCRIPTORS)
        amenity = rng.choice(_AMENITIES)
        amenities = rng.sample(_AMENITIES, k=3)
        term = rng.choice(_TERMS)
        street, base_lat, base_lng, neighborhood = rng.choice(_NEIGHBORHOODS)

        # Build a unique title.
        for attempt in range(8):
            template = rng.choice(_TITLE_TEMPLATES)
            raw = template.format(
                descriptor=descriptor,
                phrase=phrase,
                neighborhood=neighborhood,
                street=street,
                term=term,
                amenity=amenity,
            )
            title = raw[0].upper() + raw[1:] if raw else raw
            if title not in used_titles:
                break
            descriptor = rng.choice(_DESCRIPTORS)
        else:
            # Last-resort suffix to guarantee uniqueness.
            title = f"{title} #{i + 1}"
        used_titles.add(title)

        house_no = rng.randint(2800, 7400)
        location = f"{house_no} {street}, San Diego, CA"
        lat = round(base_lat + rng.uniform(-0.0045, 0.0045), 6)
        lng = round(base_lng + rng.uniform(-0.0045, 0.0045), 6)

        price_lo, price_hi = _PRICE_RANGES[room_type]
        price = float(rng.randint(price_lo // 25, price_hi // 25) * 25)
        sqft_lo, sqft_hi = _SQFT_RANGES[room_type]
        sqft = rng.randint(sqft_lo, sqft_hi)

        minutes = rng.randint(2, 25)
        desc_template = rng.choice(_DESCRIPTION_TEMPLATES)
        description = desc_template.format(
            descriptor=descriptor,
            descriptor_lower=descriptor.lower(),
            phrase=phrase,
            phrase_cap=phrase[0].upper() + phrase[1:],
            neighborhood=neighborhood,
            street=street,
            term=term,
            term_sentence=f"Lease runs {term}",
            minutes=minutes,
            amenity1=amenities[0],
            amenity2=amenities[1],
            amenity3=amenities[2],
            amenity1_cap=amenities[0][0].upper() + amenities[0][1:],
            audience=rng.choice(_AUDIENCES),
            audience_sentence=f"Best for {rng.choice(_AUDIENCES)}",
            nearby=rng.choice(_NEARBY),
        )

        out.append(
            {
                "owner": owner,
                "title": title,
                "description": description,
                "price": price,
                "location": location,
                "room_type": room_type,
                "sqft": sqft,
                "latitude": lat,
                "longitude": lng,
                "college_id": SDSU_COLLEGE_ID,
                "image_urls": _placeholder_images(rng, i),
            }
        )
    return out


GENERATED_LISTINGS: list[dict] = _generate_listings(
    user_pool=[u["username"] for u in ALL_DEMO_USERS],
    count=GENERATED_COUNT,
    seed=RNG_SEED,
    forbidden_titles={spec["title"] for spec in DEMO_LISTINGS},
)

ALL_LISTINGS: list[dict] = DEMO_LISTINGS + GENERATED_LISTINGS


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------


def upsert_users(db) -> dict[str, User]:
    """Create demo users (and their profiles) if they don't already exist."""
    by_username: dict[str, User] = {}
    pwd = hash_password(DEMO_PASSWORD)

    for spec in ALL_DEMO_USERS:
        existing = db.query(User).filter(User.email == spec["email"]).first()
        if existing:
            by_username[spec["username"]] = existing
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

    for i, spec in enumerate(ALL_LISTINGS):
        owner = users_by_username[spec["owner"]]

        already = (
            db.query(Listing)
            .filter(Listing.host_id == owner.id, Listing.title == spec["title"])
            .first()
        )
        if already:
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
            college_id=spec.get("college_id", SDSU_COLLEGE_ID),
            thumbnail_url=urls[0],
            image_urls=urls,
            latitude=spec["latitude"],
            longitude=spec["longitude"],
        )
        db.add(listing)
        created += 1

    db.commit()
    return created


def main() -> None:
    Base.metadata.create_all(bind=engine)  # safety net if DB is fresh
    db = SessionLocal()
    try:
        print(f"Seeding {len(ALL_DEMO_USERS)} users…")
        users = upsert_users(db)
        print(f"\nSeeding {len(ALL_LISTINGS)} listings…")
        new_listings = upsert_listings(db, users)

        print("\nDone.")
        print(f"  users in DB: {len(users)}")
        print(f"  listings created this run: {new_listings}")
        print(f"  total listings defined: {len(ALL_LISTINGS)}")
        print(f"\nLog in with any of these emails / password '{DEMO_PASSWORD}':")
        for spec in DEMO_USERS:
            print(f"  · {spec['email']}  ({spec['username']})")
        print(f"  …plus {len(EXTRA_USERS)} more at <username>.demo@example.com")
    finally:
        db.close()


if __name__ == "__main__":
    main()
