import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app
from app.database import get_db
from app.models import User, MedicalRecord

def clean_data():
    app = create_app()
    
    with app.app_context():
        db = get_db()
        
        test_user = db.query(User).filter(User.username == "testuser").first()
        if test_user:
            print(f"Removing user: {test_user.username} and associated records...")
            # Records should be deleted by cascade or manually
            db.query(MedicalRecord).filter(MedicalRecord.user_id == test_user.id).delete()
            db.delete(test_user)
            db.commit()
            print("Data cleaned successfully.")
        else:
            print("Test user not found. Nothing to clean.")

if __name__ == "__main__":
    clean_data()
