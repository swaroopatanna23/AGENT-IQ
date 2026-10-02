from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.users import User
from app.auth.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        # Provide default demo user for seamless academic testing if no token provided
        demo_user = db.query(User).filter(User.email == "demo@agentiq.ai").first()
        if not demo_user:
            demo_user = User(
                email="demo@agentiq.ai",
                hashed_password="demo_hashed_placeholder",
                full_name="AgentIQ Researcher",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        return demo_user

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user
