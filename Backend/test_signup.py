import sys
sys.path.insert(0, '.')

from app.database import get_db
from app import models
from app.security import hash_password
from uuid import uuid4

try:
    db = next(get_db())
    
    # Test creating a user
    test_email = f"test_{uuid4().hex[:8]}@example.com"
    print(f"Testing signup with email: {test_email}")
    
    # Check if user exists
    existing = db.query(models.User.id).filter(models.User.email == test_email).first()
    if existing:
        print("User already exists")
    else:
        print("Creating new user...")
        user = models.User(
            id=str(uuid4()),
            name="Test User",
            email=test_email,
            password_hash=hash_password("test123"),
            role='user'
        )
        db.add(user)
        print("User added to session, committing...")
        db.commit()
        print("✅ Commit successful!")
        
        # Query back
        user_data = db.query(
            models.User.id,
            models.User.name,
            models.User.email
        ).filter(models.User.id == user.id).first()
        
        if user_data:
            print(f"✅ User created successfully!")
            print(f"   ID: {user_data.id}")
            print(f"   Name: {user_data.name}")
            print(f"   Email: {user_data.email}")
        else:
            print("❌ User not found after commit")
    
    db.close()
    
except Exception as e:
    import traceback
    print(f"❌ Error: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()


