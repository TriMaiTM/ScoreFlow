
import asyncio
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_superuser():
    email = input("Enter admin email (default: admin@example.com): ") or "admin@example.com"
    password = input("Enter admin password (default: admin123): ") or "admin123"
    
    async with AsyncSessionLocal() as db:
        # Check if exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User {email} already exists. Updating to superuser...")
            user.hashed_password = get_password_hash(password)
            user.is_superuser = True
            user.is_active = True
        else:
            print(f"Creating new superuser {email}...")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                name="System Admin",
                is_active=True,
                is_superuser=True
            )
            db.add(user)
            
        await db.commit()
        print("✅ Superuser created successfully!")
        print(f"👉 Login with: {email} / {password}")

if __name__ == "__main__":
    asyncio.run(create_superuser())
