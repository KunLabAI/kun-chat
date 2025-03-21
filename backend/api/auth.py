from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from database import Database, get_db
import sys
import os
import json
import jwt
import logging
import bcrypt
import shutil
import uuid
from pathlib import Path

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ERROR_MESSAGES, SECURITY_CONFIG

logger = logging.getLogger(__name__)

# 密码验证规则
PASSWORD_RULES = {
    "length": 6,
    "allowed_chars": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
}

# 自定义错误类型
class AuthError:
    class InvalidCredentials(HTTPException):
        def __init__(self):
            super().__init__(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
    
    class TokenExpired(HTTPException):
        def __init__(self):
            super().__init__(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="登录已过期，请重新登录"
            )
    
    class TokenInvalid(HTTPException):
        def __init__(self):
            super().__init__(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的登录凭证"
            )
    
    class UserExists(HTTPException):
        def __init__(self):
            super().__init__(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None

class UserCreate(UserBase):
    password: str
    security_question: Optional[str] = None
    security_answer: Optional[str] = None

class User(UserBase):
    created_at: datetime
    model_config = {
        'from_attributes': True
    }

class UserInfo(UserBase):
    model_config = {
        'from_attributes': True
    }

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class UserPreferences(BaseModel):
    # 用户昵称
    nickname: Optional[str] = None
    # 用户个人信息和偏好设置
    personal_info: Optional[str] = None
    # 是否在对话中使用个人信息
    use_personal_info: Optional[bool] = True

class SecurityQuestionVerify(BaseModel):
    username: str
    answer: Optional[str] = None

class PasswordReset(BaseModel):
    username: str
    new_password: str

class EmailUpdate(BaseModel):
    email: EmailStr

class EmailVerify(BaseModel):
    username: str
    email: EmailStr

class UserProfile(BaseModel):
    nickname: Optional[str] = None

# Security functions
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 确保hashed_password是bytes类型
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bcrypt.checkpw(plain_password.encode(), hashed_password)

def get_password_hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

async def get_user(db: Database, username: str) -> Optional[Dict]:
    return await db.fetch_one(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

async def authenticate_user(db: Database, username: str, password: str) -> Optional[Dict]:
    user = await get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, persistent: bool = False) -> str:
    to_encode = data.copy()
    if persistent:
        expire = datetime.utcnow() + timedelta(days=SECURITY_CONFIG["PERSISTENT_TOKEN_EXPIRE_DAYS"])
    elif expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SECURITY_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"])
    to_encode.update({"exp": expire})
    if persistent:
        to_encode.update({"persistent": True})
    encoded_jwt = jwt.encode(to_encode, SECURITY_CONFIG["SECRET_KEY"], algorithm=SECURITY_CONFIG["ALGORITHM"])
    return encoded_jwt

def create_persistent_token(username: str) -> str:
    return create_access_token({"sub": username}, persistent=True)

def should_refresh_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECURITY_CONFIG["SECRET_KEY"], algorithms=[SECURITY_CONFIG["ALGORITHM"]])
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # 计算token的总有效期和剩余有效期
        if "persistent" in payload and payload["persistent"]:
            total_valid_time = timedelta(days=SECURITY_CONFIG["PERSISTENT_TOKEN_EXPIRE_DAYS"])
        else:
            total_valid_time = timedelta(minutes=SECURITY_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"])
        
        remaining_time = exp - now
        
        # 当剩余有效期小于25%时刷新token
        return remaining_time < (total_valid_time / 4)
    except:
        return True

def refresh_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECURITY_CONFIG["SECRET_KEY"], algorithms=[SECURITY_CONFIG["ALGORITHM"]])
        persistent = "persistent" in payload and payload["persistent"]
        return create_access_token({"sub": payload["sub"]}, persistent=persistent)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的登录凭证"
        )

def decode_token(token: str) -> Dict[str, Any]:
    """
    解码并验证 JWT token
    """
    try:
        payload = jwt.decode(token, SECURITY_CONFIG["SECRET_KEY"], algorithms=[SECURITY_CONFIG["ALGORITHM"]])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["invalid_token"]
            )
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["invalid_token"]
        )

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    返回: (是否通过验证, 错误信息)
    """
    if len(password) != PASSWORD_RULES["length"]:
        return False, f"密码长度必须为{PASSWORD_RULES['length']}个字符"
    
    if not all(c in PASSWORD_RULES["allowed_chars"] for c in password):
        return False, "密码只能包含英文字母和数字"
    
    return True, ""

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db)
) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECURITY_CONFIG["SECRET_KEY"], algorithms=[SECURITY_CONFIG["ALGORITHM"]])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = await get_user(db, username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=dict)
async def register_user(user: UserCreate, db: Database = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = await db.fetch_one(
        "SELECT username FROM users WHERE username = ?",
        (user.username,)
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="用户名或邮箱已被使用"
        )

    # 如果提供了email，检查是否已被使用
    if user.email:
        existing_email = await db.fetch_one(
            "SELECT username FROM users WHERE email = ?",
            (user.email,)
        )
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="用户名或邮箱已被使用"
            )

    valid, error = validate_password_strength(user.password)
    if not valid:
        raise HTTPException(
            status_code=400,
            detail=error
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    nickname = user.username
    try:
        await db.execute(
            """
            INSERT INTO users (
                username, nickname, email, hashed_password, 
                security_question, security_answer,
                preferences, last_login
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.username, nickname, user.email, hashed_password,
                user.security_question or "", user.security_answer or "",
                json.dumps({}), datetime.utcnow()
            )
        )
        await db.commit()
        
        # 创建token
        token = create_access_token({"sub": user.username})
        
        return {
            "username": user.username,
            "nickname": nickname,
            "token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="注册失败，请稍后重试"
        )

@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    await db.execute(
        "UPDATE users SET last_login = ? WHERE username = ?",
        (datetime.utcnow(), user["username"])
    )
    await db.commit()
    
    access_token = create_access_token({"sub": user["username"]})
    return {
        "username": user["username"],
        "nickname": user.get("nickname", user["username"]),
        "email": user.get("email", ""),
        "avatar": user.get("avatar", ""),
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/token", response_model=dict)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    """
    OAuth2 兼容的令牌获取接口
    """
    return await login(form_data, db)

@router.post("/auto-login")
async def auto_login(token: str, db: Database = Depends(get_db)):
    """
    自动登录接口
    - 验证token有效性
    - 检查是否需要刷新token
    - 更新最后登录时间
    """
    try:
        # 验证token并获取用户信息
        user = await get_current_user(token, db)
        new_token = token
        
        # 检查是否需要刷新token
        if should_refresh_token(token):
            new_token = refresh_token(token)
        
        # 更新最后登录时间
        await db.execute(
            "UPDATE users SET last_login = ? WHERE username = ?",
            (datetime.utcnow(), user["username"])
        )
        await db.commit()
        
        return {
            "username": user["username"],
            "nickname": user.get("nickname", user["username"]),
            "email": user.get("email", ""),
            "avatar": user.get("avatar", ""),
            "token": new_token,
            "token_type": "bearer",
            "token_refreshed": new_token != token
        }
    except jwt.ExpiredSignatureError:
        raise AuthError.TokenExpired()
    except jwt.JWTError:
        raise AuthError.TokenInvalid()
    except Exception as e:
        logger.error(f"Auto-login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统错误，请稍后重试"
        )

@router.get("/me", response_model=UserInfo)
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    # 验证当前密码
    if not verify_password(password_data.current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新密码
    new_hashed_password = get_password_hash(password_data.new_password)
    await db.execute(
        "UPDATE users SET hashed_password = ? WHERE username = ?",
        (new_hashed_password, current_user["username"])
    )
    await db.commit()
    
    return {"message": "密码更新成功"}

@router.get("/preferences")
async def get_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    prefs = await db.fetch_one(
        "SELECT preferences FROM users WHERE username = ?",
        (current_user["username"],)
    )
    return json.loads(prefs["preferences"] or "{}")

@router.post("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    await db.execute(
        "UPDATE users SET preferences = ? WHERE username = ?",
        (json.dumps(preferences.dict()), current_user["username"])
    )
    await db.commit()
    return {"message": "偏好设置更新成功"}

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db)
):
    logger.info(f"尝试登录用户: {form_data.username}")
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"用户登录失败: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"用户登录成功: {form_data.username}")
    access_token = create_access_token({"sub": user["username"]})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user["username"],
        "nickname": user.get("nickname", user["username"]),
        "email": user.get("email", ""),
        "avatar": user.get("avatar", "")
    }

async def verify_security_question_handler(username: str, answer: str = None, db: Database = Depends(get_db)) -> dict:
    """验证用户的安全问题"""
    # 获取用户的安全问题
    user = await db.fetch_one(
        "SELECT username, security_question, security_answer FROM users WHERE username = ?",
        (username,)
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 如果没有提供答案，只返回安全问题
    if answer is None:
        return {"securityQuestion": user["security_question"]}

    # 验证答案
    if user["security_answer"].lower() != answer.lower():
        raise HTTPException(status_code=400, detail="安全问题答案不正确")

    return {"verified": True}

async def reset_password_handler(username: str, new_password: str, db: Database = Depends(get_db)) -> dict:
    """重置用户密码"""
    # 验证邮箱
    user = await db.fetch_one(
        "SELECT username, email FROM users WHERE username = ?",
        (username,)
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 验证邮箱
    if not user["email"]:
        raise HTTPException(status_code=400, detail="用户未绑定邮箱")

    # 生成新的密码哈希
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode(), salt)
    
    # 更新密码
    await db.execute(
        "UPDATE users SET hashed_password = ? WHERE username = ?",
        (hashed_password, username)
    )
    await db.commit()

    return {"message": "密码重置成功"}

async def verify_email_for_reset_handler(username: str, email: str, db: Database = Depends(get_db)) -> dict:
    """验证用户的邮箱地址"""
    # 获取用户的邮箱
    user = await db.fetch_one(
        "SELECT username, email FROM users WHERE username = ?",
        (username,)
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 验证邮箱
    if not user["email"] or user["email"].lower() != email.lower():
        raise HTTPException(status_code=400, detail="邮箱地址不正确")

    return {"verified": True}

@router.post("/verify-email-reset")
async def verify_email_reset_route(data: EmailVerify, db: Database = Depends(get_db)):
    """验证用户的邮箱地址用于重置密码"""
    return await verify_email_for_reset_handler(data.username, data.email, db)

@router.post("/verify-security-question")
async def verify_security_question_route(data: SecurityQuestionVerify, db: Database = Depends(get_db)):
    """验证用户的安全问题"""
    return await verify_security_question_handler(data.username, data.answer, db)

@router.post("/reset-password")
async def reset_password_route(data: PasswordReset, db: Database = Depends(get_db)):
    """重置用户密码"""
    return await reset_password_handler(data.username, data.new_password, db)

@router.post("/update-email", response_model=Dict[str, Any])
async def update_email(
    email_data: EmailUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新用户邮箱
    """
    try:
        # 检查邮箱是否已被使用
        existing_user = await db.fetch_one(
            """
            SELECT username FROM users
            WHERE email = ? AND username != ?
            """,
            (email_data.email, current_user["username"])
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他用户使用"
            )
        
        # 更新邮箱
        await db.execute(
            """
            UPDATE users
            SET email = ?
            WHERE username = ?
            """,
            (email_data.email, current_user["username"])
        )
        
        return {
            "status": "success",
            "message": "邮箱已更新"
        }
    except Exception as e:
        logger.error(f"更新邮箱失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新邮箱失败"
        )

@router.post("/avatar", response_model=Dict[str, Any])
async def update_avatar(
    avatar: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新用户头像
    """
    try:
        # 验证文件类型
        content_type = avatar.content_type
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只允许上传图片文件"
            )
        
        # 创建上传目录
        upload_dir = Path("static/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        file_extension = avatar.filename.split(".")[-1] if "." in avatar.filename else "jpg"
        unique_filename = f"{current_user['username']}_{uuid.uuid4()}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        # 保存文件
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        
        # 生成访问URL (确保以/开头)
        avatar_url = f"/static/avatars/{unique_filename}"
        
        # 更新数据库
        await db.execute(
            """
            UPDATE users
            SET avatar = ?
            WHERE username = ?
            """,
            (avatar_url, current_user["username"])
        )
        
        return {
            "status": "success",
            "message": "头像已更新",
            "avatar_url": avatar_url
        }
    except Exception as e:
        logger.error(f"更新头像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新头像失败: {str(e)}"
        )

# 更新用户资料
@router.put("/profile")
async def update_profile(
    profile_data: UserProfile,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新用户资料
    """
    try:
        username = current_user["username"]
        
        # 更新用户资料
        updates = {}
        if profile_data.nickname is not None:
            updates["nickname"] = profile_data.nickname
            
        if not updates:
            return {"message": "没有需要更新的资料"}
            
        # 构建更新SQL
        update_fields = ", ".join([f"{field} = ?" for field in updates.keys()])
        values = list(updates.values())
        values.append(username)
        
        # 执行更新
        await db.ensure_connected()
        await db._connection.execute(
            f"UPDATE users SET {update_fields} WHERE username = ?",
            values
        )
        await db._connection.commit()
        
        return {"message": "资料更新成功", "updated_fields": list(updates.keys())}
    except Exception as e:
        logger.error(f"更新用户资料失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )
