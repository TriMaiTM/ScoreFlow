
import asyncio
import sys
import traceback
from app.db.database import get_db, engine
from app.db.models import User
from app.core.security import get_password_hash
from app.schemas.schemas import UserCreate
from sqlalchemy import select

async def test_register():
    print("Starting registration debug...")
    
    # Mock data
    user_data = UserCreate(
        name="Test Debug User",
        email="debug_user@example.com",
        password="password123",
        confirmPassword="password123"
    )
    
    print(f"Data: {user_data}")
    
    async with engine.begin() as conn:
        # Check if user exists (to clean up if needed from previous runs)
        pass 

    # Manual session
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # 1. Check existing
            print("Checking existing user...")
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing = result.scalar_one_or_none()
            if existing:
                print("User already exists. Deleting for test...")
                await db.delete(existing)
                await db.commit()
            
            # 2. Logic from auth.py
            print("Hashing password...")
            hashed_password = get_password_hash(user_data.password)
            
            print("Creating User object...")
            new_user = User(
                email=user_data.email,
                name=user_data.name,
                hashed_password=hashed_password,
                # is_superuser defaults to False
            )
            
            print("Adding to DB...")
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            print(f"✅ Success! User created with ID: {new_user.id}")
            
        except Exception as e:
            print("\n❌ ERROR DETECTED:")
            traceback.print_exc()

if __name__ == "__main__":
    # Ensure app context if needed (settings etc)
    asyncio.run(test_register())
