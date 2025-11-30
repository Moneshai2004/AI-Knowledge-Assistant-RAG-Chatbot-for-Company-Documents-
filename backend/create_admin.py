# create_admin.py
import asyncio
from app.db.session import async_session
from app.models.admin_user import AdminUser
from app.services.passwords import hash_password

async def create_admin():
    async with async_session() as session:
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin123")
        )
        session.add(admin)
        await session.commit()

asyncio.run(create_admin())
