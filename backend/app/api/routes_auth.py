from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.db.session import async_session
from app.models.admin_user import AdminUser
from app.services.passwords import verify_password, hash_password
from app.services.jwt_handler import create_jwt, auth_required

router = APIRouter(prefix="/auth", tags=["Auth"])

# --------------------------------------
# ADMIN LOGIN
# --------------------------------------
@router.post("/login")
async def login(username: str, password: str):
    async with async_session() as session:
        q = await session.execute(
            select(AdminUser).where(AdminUser.username == username)
        )
        user = q.scalar()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

        token = create_jwt({"id": user.id, "username": user.username, "role": "admin"})
        return {"token": token}

# --------------------------------------
# GET CURRENT USER
# --------------------------------------
@router.get("/me")
async def get_me(user=Depends(auth_required)):
    return user
