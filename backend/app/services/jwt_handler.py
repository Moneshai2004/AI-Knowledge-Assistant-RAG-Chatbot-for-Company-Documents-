import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET = "SUPER_SECRET_KEY_CHANGE_THIS"  # replace in production
ALGO = "HS256"
security = HTTPBearer()

def create_jwt(data: dict, expires_minutes: int = 24 * 60):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload["iat"] = datetime.utcnow()
    return jwt.encode(payload, SECRET, ALGO)

def verify_jwt(token: str):
    try:
        decoded = jwt.decode(token, SECRET, algorithms=[ALGO])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def auth_required(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_jwt(token)
