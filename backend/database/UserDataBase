from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


DataBase_URL = "sqlite:///database.db"
engine = create_engine(DataBase_URL, echo=True)

Base = declarative_base()

#Defining the Model

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    balance = Column(Float)
    password = Column(String) 
    points = Column(Integer)
    tier = Column(String)

#Create tables
Base.metadata.create_all(engine)  

#Create Session
Session = sessionmaker(bind=engine)
session = Session()

#User Database Operations
def create_user(username, email, password):
    """Create a new user in the database"""
    default_balance = 20
    default_tier = "Silver"
    default_points = 0
    try:
        new_user = User(name=username, email=email, password=password, balance=default_balance, tier=default_tier, points=default_points)
        session.add(new_user)
        session.commit()
        return new_user
    except IntegrityError:
        session.rollback()
        return None
    except Exception as e:
        session.rollback()
        print(f"Error creating user: {e}")
        return None

def get_user_by_email(email):
    """Get user by email address"""
    try:
        return session.query(User).filter_by(email=email).first()
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        return session.query(User).filter_by(id=user_id).first()
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None
    
def get_user_balance(user_email):
    """Get user balance by account number"""
    try:
        return session.query(User).filter_by(email=user_email).first().balance
    
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None
    
    # # Update

def update_user_balance(user_email, new_balance):

    try:
        user = session.query(User).filter_by(email=user_email).first()
        user.balance = new_balance
        session.commit()

    except Exception as e:
        print(f"Error updating user: {e}")
        return None

# delete 

def delete(user):
     
    try:
        session.delete(user)
        session.commit()

    except Exception as e:
        print(f"Error deleting user: {e}")
        return None
    