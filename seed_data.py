from datetime import datetime
from app import create_app
from app.models import db, User, Treks, Bookings

app = create_app()

TREKS = [
    {
        "name": "Kedarnath Trek", "location": "Uttarakhand, India",
        "description": "A sacred and breathtaking trek to the ancient Kedarnath temple nestled amidst the mighty Himalayas. The trail passes through lush meadows, gushing rivers and serene valleys.",
        "difficulty": "Moderate", "duration": 5, "capacity": 20, "available": 15,
        "price": 8500, "altitude": "3583m", "starting_date": "2026-05-10", "ending_date": "2026-05-14",
        "image_url": "https://images.unsplash.com/photo-1622308644420-b20142dc993c?w=800",
        "highlights": "Ancient Kedarnath Temple\nMesmerizing Himalayan views\nVasuki Tal Lake\nGandhi Sarovar",
        "requirements": "Moderate fitness level\nTrekking boots\nWarm layered clothing\nRain gear",
    },
    {
        "name": "Valley of Flowers", "location": "Chamoli, Uttarakhand",
        "description": "A UNESCO World Heritage trek through an enchanting valley bursting with alpine flowers and rare wildlife.",
        "difficulty": "Easy", "duration": 4, "capacity": 25, "available": 20,
        "price": 6000, "altitude": "3658m", "starting_date": "2026-06-15", "ending_date": "2026-06-18",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        "highlights": "300+ flower species\nNanda Devi views\nHemkund Sahib nearby\nWildlife sightings",
        "requirements": "Basic fitness\nComfortable walking shoes\nCamera\nSunscreen and hat",
    },
    {
        "name": "Roopkund Trek", "location": "Chamoli, Uttarakhand",
        "description": "One of India's most mysterious treks leading to the skeletal lake at 5029m, with dramatic views of Trishul and Nanda Ghunti peaks.",
        "difficulty": "Hard", "duration": 8, "capacity": 15, "available": 8,
        "price": 14000, "altitude": "5029m", "starting_date": "2026-07-01", "ending_date": "2026-07-08",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800",
        "highlights": "Mysterious skeleton lake\nTrishul peak views\nBedni Bugyal meadows\nHigh altitude flora",
        "requirements": "High fitness level\nPrevious trekking experience\nWarm insulated gear\nAltitude medication",
    },
    {
        "name": "Hampta Pass", "location": "Kullu, Himachal Pradesh",
        "description": "A dramatic crossover trek from the lush Kullu valley to the barren Lahaul landscape.",
        "difficulty": "Moderate", "duration": 5, "capacity": 18, "available": 12,
        "price": 9500, "altitude": "4270m", "starting_date": "2026-07-10", "ending_date": "2026-07-14",
        "image_url": "https://images.unsplash.com/photo-1551632811-561732d1e306?w=800",
        "highlights": "Dramatic landscape contrast\nChandratal Lake visit\nSnowy pass crossing\nCamping by streams",
        "requirements": "Moderate fitness\nCamping gear provided\nWarm layers\nTrekking poles",
    },
    {
        "name": "Triund Trek", "location": "Dharamshala, Himachal Pradesh",
        "description": "An easy and rewarding trek from McLeod Ganj to the Triund hilltop, with views of the Dhauladhar range.",
        "difficulty": "Easy", "duration": 2, "capacity": 30, "available": 22,
        "price": 2500, "altitude": "2875m", "starting_date": "2026-04-20", "ending_date": "2026-04-21",
        "image_url": "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800",
        "highlights": "Dhauladhar range panorama\nSunrise over the Himalayas\nTibetan culture exposure\nCampfire under the stars",
        "requirements": "Basic fitness\nLight backpack\nComfort shoes\nCash for local vendors",
    },
    {
        "name": "Pin Parvati Pass", "location": "Kullu & Spiti, Himachal Pradesh",
        "description": "One of the most challenging and remote treks in India, crossing the formidable Pin Parvati Pass.",
        "difficulty": "Hard", "duration": 11, "capacity": 10, "available": 6,
        "price": 22000, "altitude": "5319m", "starting_date": "2026-08-15", "ending_date": "2026-08-25",
        "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800",
        "highlights": "Mantalai Lake basecamp\nGlacier crossings\nWild river crossings\nPin Valley desert landscape",
        "requirements": "Excellent fitness\nMultiple previous high-altitude treks\nFull camping equipment\nEmergency medical kit",
    },
]

STAFF = [
    {"name": "rajan_guide", "full_name": "Rajan Sharma", "email": "rajan@trek.com", "contact": "9876543210"},
    {"name": "meera_trek", "full_name": "Meera Patel", "email": "meera@trek.com", "contact": "9876543211"},
]

USERS = [
    {"name": "arjun99", "full_name": "Arjun Mehta", "email": "arjun@example.com", "contact": "9812345678"},
    {"name": "priya_hiker", "full_name": "Priya Kapoor", "email": "priya@example.com", "contact": "9823456789"},
    {"name": "ani_adventures", "full_name": "Aniket Sharma", "email": "aniket@example.com", "contact": "9834567890"},
]


def seed():
    with app.app_context():
        staff_users = []
        for s in STAFF:
            user = User.query.filter_by(name=s["name"]).first()
            if not user:
                user = User(full_name=s["full_name"], name=s["name"], email=s["email"],
                            contact=s["contact"], role="staff", is_approved=True)
                user.set_pass_hash("123456")
                db.session.add(user)
                db.session.commit()
                # print(f"Created staff: {s['name']}")
            staff_users.append(user)

        trekkers = []
        for u in USERS:
            user = User.query.filter_by(name=u["name"]).first()
            if not user:
                user = User(full_name=u["full_name"], name=u["name"], email=u["email"],
                            contact=u["contact"], role="trekker")
                user.set_pass_hash("123456")
                db.session.add(user)
                db.session.commit()
                # print(f"Created user: {u['name']}")
            trekkers.append(user)

        treks = []
        for i, t in enumerate(TREKS):
            trek = Treks.query.filter_by(name=t["name"]).first()
            if not trek:
                trek = Treks(
                    name=t["name"], location=t["location"], description=t["description"],
                    difficulty=t["difficulty"], duration=t["duration"], capacity=t["capacity"],
                    available=t["available"], price=t["price"], altitude=t["altitude"],
                    starting_date=datetime.strptime(t["starting_date"], "%Y-%m-%d").date(),
                    ending_date=datetime.strptime(t["ending_date"], "%Y-%m-%d").date(),
                    status="Open", image_url=t["image_url"], highlights=t["highlights"],
                    requirements=t["requirements"], assigned_staff_id=staff_users[i % len(staff_users)].id,
                )
                db.session.add(trek)
                db.session.commit()
                # print(f"Created trek: {t['name']}")
            treks.append(trek)

        sample_bookings = [
            (trekkers[0], treks[0], 1, "Mrs Mehta", "9800000001", "Vegetarian meals preferred"),
            (trekkers[1], treks[1], 1, "Mr Kapoor", "9800000002", ""),
            (trekkers[2], treks[0], 1, "Mr Khan Sr", "9800000003", "Mild knee issue"),
            (trekkers[0], treks[4], 1, "Mrs Mehta", "9800000001", ""),
        ]
        for user, trek, parts, contact, phone, notes in sample_bookings:
            existing = Bookings.query.filter_by(user_id=user.id, trek_id=trek.id).first()
            if not existing:
                booking = Bookings(user_id=user.id, trek_id=trek.id, participants=parts,
                                    emergency_contact=contact, emergency_phone=phone,
                                    notes=notes, status="Booked")
                db.session.add(booking)
                db.session.commit()
                print(f"Created booking: {user.name} -> {trek.name}")

        print("\nLogin credentials:")
        for s in STAFF:
            print(f"  Staff : {s['email']} / 123456")
        for u in USERS:
            print(f"  User  : {u['email']} / 123456")


if __name__ == "__main__":
    seed()
