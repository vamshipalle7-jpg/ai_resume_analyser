from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.database import db_service
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
async def register(user_in: UserCreate):
    existing = db_service.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    hashed = hash_password(user_in.password)
    user = db_service.create_user(
        email=user_in.email,
        hashed_password=hashed,
        full_name=user_in.full_name or "Job Seeker",
        role="user"
    )

    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"], "role": user.get("role", "user")}
    )

    db_service.log_audit(user["id"], "USER_REGISTERED", {"email": user["email"]})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            role=user.get("role", "user"),
            created_at=user.get("created_at", "")
        )
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    user = db_service.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"], "role": user.get("role", "user")}
    )

    db_service.log_audit(user["id"], "USER_LOGIN", {"email": user["email"]})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            role=user.get("role", "user"),
            created_at=user.get("created_at", "")
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        role=current_user.get("role", "user"),
        created_at=current_user.get("created_at", "")
    )
