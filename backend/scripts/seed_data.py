import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app
from app.database import init_db, get_db
from app.models import User, MedicalRecord
from app.utils.security import get_password_hash

def seed_data():
    app = create_app()
    
    with app.app_context():
        print("Initializing database...")
        init_db()
        db = get_db()
        
        # Check if test user exists
        test_user = db.query(User).filter(User.username == "testuser").first()
        if test_user:
            print("Test user already exists.")
        else:
            print("Creating test user...")
            test_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                hashed_password=get_password_hash("password123")
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"User created: {test_user.username}")

        # Add some medical records
        if db.query(MedicalRecord).filter(MedicalRecord.user_id == test_user.id).count() == 0:
            print("Adding medical records...")
            records = [
                MedicalRecord(
                    user_id=test_user.id,
                    title="Annual Checkup",
                    original_text="Patient presents with mild fatigue. BP 120/80. Recommended more sleep.",
                    record_type="doctor_note"
                ),
                MedicalRecord(
                    user_id=test_user.id,
                    title="Blood Test Results",
                    original_text="Hemoglobin: 14.5 g/dL, WBC: 6.5, Platelets: 250. All within normal range.",
                    record_type="lab_result"
                )
            ]
            db.add_all(records)
            db.commit()
            print(f"Added {len(records)} medical records.")
        else:
            print("Medical records already exist.")

if __name__ == "__main__":
    seed_data()
