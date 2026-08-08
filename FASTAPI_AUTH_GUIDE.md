# 🛡️ Hướng Dẫn Lập Trình Hệ Thống Auth (Xác Thực & Phân Quyền) Hoàn Chỉnh Với FastAPI & SQLModel

Tài liệu này hướng dẫn chi tiết cách triển khai tính năng Xác thực (**Authentication**) và Phân quyền (**Authorization**) chuẩn production cho ứng dụng Backend với **FastAPI**, **SQLModel**, **JWT Token** và **Password Hashing** theo kiến trúc phân tầng (Clean / Layered Architecture).

---

## 📁 Cấu Trúc Thư Mục Dự Án (Project Structure)

```text
app/
├── core/
│   ├── config.py         # Cấu hình biến môi trường, JWT Secret Key
│   └── security.py       # Hàm Hash mật khẩu và Tạo/Mã hóa JWT Token
├── db/
│   └── database.py       # Kết nối SQLite/PostgreSQL & tạo Session DB
├── models/
│   └── user.py           # SQLModel Entity đại diện cho bảng 'user' trong DB
├── schemas/
│   └── user.py           # Pydantic Schemas validate dữ liệu Request/Response
├── repositories/
│   └── user_repository.py# Tầng tương tác trực tiếp với Database (CRUD)
├── services/
│   └── auth_service.py   # Tầng xử lý logic nghiệp vụ Đăng ký & Đăng nhập
├── dependencies/
│   └── auth.py           # FastAPI Dependency kiểm tra & trích xuất User từ JWT Token
├── routers/
│   └── auth.py           # Các API Endpoints (/register, /login, /me)
└── main.py               # Khởi tạo ứng dụng FastAPI và nhúng Router
```

---

## 🛠️ 1. Cấu Hình Bí Mật & Môi Trường (`app/core/config.py`)

Tệp này quản lý tập trung các hằng số bảo mật, thời gian hết hạn của token, và khóa bí mật.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus OMS"
    SECRET_KEY: str = "your-super-secret-key-change-it-in-production-123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./nexus_oms.db"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 💡 Giải thích tác dụng:
* **`SECRET_KEY`**: Khóa bí mật chỉ có Server biết, dùng để ký (sign) chuỗi JWT Token. Nếu khóa này bị lộ, kẻ xấu có thể tự tạo Token giả mạo.
* **`ALGORITHM`**: Thuật toán mã hóa đối xứng `HS256` (HMAC với SHA-256).
* **`ACCESS_TOKEN_EXPIRE_MINUTES`**: Thời hạn sống của Token (ví dụ: 30 phút). Hết thời gian này Token sẽ không còn hiệu lực.

---

## 🔐 2. Tiện Ích Mã Hóa Mật Khẩu & Mã Hóa JWT (`app/core/security.py`)

Tệp này đảm nhận nhiệm vụ băm mật khẩu 1 chiều và thao tác với JWT Token.

```python
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import jwt
from app.core.config import settings

# Khởi tạo đối tượng mã hóa mật khẩu theo tiêu chuẩn khuyến nghị (Argon2 / Bcrypt)
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Băm mật khẩu dạng thô (plain text) thành chuỗi băm an toàn."""
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào có trùng khớp với chuỗi băm trong DB hay không."""
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id: int) -> str:
    """Tạo chuỗi JWT Access Token chứa ID của User và thời điểm hết hạn."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),  # subject: Định danh chủ sở hữu token
        "exp": expire,        # expiration time: Thời điểm token hết hạn
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Giải mã Token và xác thực tính toàn vẹn bằng Secret Key."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
```

### 💡 Giải thích tác dụng:
* **`hash_password`**: Mật khẩu của người dùng tuyệt đối không được lưu dạng thô. Hàm này biến `12345678` thành `$argon2id$v=19$m=65536...` ngẫu nhiên có muối (salt).
* **`verify_password`**: So sánh mật khẩu thô lúc đăng nhập với chuỗi băm lưu trong DB mà không cần giải băm.
* **`create_access_token`**: Tạo ra chuỗi dạng `eyJhbGciOi...` đóng gói thông tin `user_id` và thời gian hết hạn `exp`.
* **`decode_access_token`**: Đọc dữ liệu bên trong Token. Nếu Token bị sửa đổi dù chỉ 1 ký tự, hàm sẽ quăng lỗi mã hóa.

---

## 🗄️ 3. Định Nghĩa Model Database (`app/models/user.py`)

Cấu trúc bảng lưu trữ thông tin tài khoản người dùng trong cơ sở dữ liệu.

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
```

### 💡 Giải thích tác dụng:
* **`table=True`**: Đánh dấu đây là bảng SQLModel sẽ được tạo trong Database.
* **`email`**: Đánh chỉ mục `index=True` giúp tìm kiếm nhanh, `unique=True` chặn trùng lặp tài khoản.
* **`hashed_password`**: Cột lưu chuỗi mật khẩu đã qua mã hóa.
* **`is_active`**: Cờ kiểm tra tài khoản còn hoạt động hay đã bị khóa.

---

## 📋 4. Định Nghĩa Schemas Validate Request / Response (`app/schemas/user.py`)

Kiểm tra dữ liệu đầu vào và chuẩn hóa dữ liệu trả về cho API Client.

```python
from datetime import datetime
from pydantic import EmailStr, Field, model_validator
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    """Dữ liệu nhận từ Client khi Đăng ký"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_password(self):
        """Xác nhận password và confirm_password trùng nhau."""
        if self.password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không trùng khớp")
        return self

class UserLogin(SQLModel):
    """Dữ liệu nhận từ Client khi Đăng nhập"""
    email: EmailStr
    password: str

class UserResponse(SQLModel):
    """Dữ liệu an toàn trả về cho Client (Ẩn hoàn toàn hashed_password)"""
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    created_at: datetime

class TokenResponse(SQLModel):
    """Định dạng Token trả về sau khi đăng nhập thành công"""
    access_token: str
    token_type: str = "bearer"
```

### 💡 Giải thích tác dụng:
* **`UserCreate`**: Dùng `EmailStr` tự động kiểm tra cú pháp Email. Dùng `@model_validator` bắt lỗi nếu người dùng gõ 2 mật khẩu khác nhau ngay tại bước nhận request.
* **`UserResponse`**: Loại bỏ trường `hashed_password` để đảm bảo mật khẩu băm không bao giờ lộ ra ngoài API Response.

---

## 📦 5. Tầng Repository Truy Cập Cơ Sở Dữ Liệu (`app/repositories/user_repository.py`)

Tách biệt các câu lệnh SQL / SQLModel khỏi logic nghiệp vụ.

```python
from sqlmodel import Session, select
from app.models.user import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        """Tìm tài khoản người dùng theo Email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_id(self, user_id: int) -> User | None:
        """Tìm tài khoản người dùng theo ID."""
        return self.session.get(User, user_id)

    def create(self, user: User) -> User:
        """Thêm người dùng mới vào Database."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
```

### 💡 Giải thích tác dụng:
* Thực hiện trực tiếp các thao tác CRUD với cơ sở dữ liệu (`add`, `commit`, `refresh`, `select`).

---

## ⚙️ 6. Tầng Xử Lý Logic Nghiệp Vụ (`app/services/auth_service.py`)

Nơi xử lý chính luồng Đăng ký và Đăng nhập.

```python
from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, data: UserCreate) -> UserResponse:
        """Nghiệp vụ Đăng ký tài khoản"""
        # 1. Kiểm tra xem Email đã có trong hệ thống chưa
        existing_user = self.user_repository.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email này đã được đăng ký trên hệ thống"
            )

        # 2. Hash mật khẩu
        hashed_pwd = hash_password(data.password)

        # 3. Khởi tạo đối tượng User
        user = User(
            email=data.email,
            hashed_password=hashed_pwd,
            full_name=None
        )

        # 4. Lưu xuống Database
        created_user = self.user_repository.create(user)

        # 5. Trả về thông tin dạng UserResponse
        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
            is_active=created_user.is_active,
            created_at=created_user.created_at
        )

    def login(self, data: UserLogin) -> TokenResponse:
        """Nghiệp vụ Đăng nhập & Cấp phát JWT Access Token"""
        # 1. Tìm user theo Email
        user = self.user_repository.get_by_email(data.email)
        
        # 2. Xác thực sai Email HOẶC Mật khẩu
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Kiểm tra tài khoản có bị vô hiệu hóa hay không
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản này hiện đang bị khóa"
            )

        # 4. Tạo JWT Token chứa User ID
        token = create_access_token(user_id=user.id)

        # 5. Trả về Token cho Client
        return TokenResponse(access_token=token, token_type="bearer")
```

### 💡 Giải thích tác dụng:
* **Kiểm tra trùng lặp**: Báo lỗi `400` nếu email đã đăng ký.
* **Bảo mật phản hồi lỗi đăng nhập**: Báo chung lỗi `401 Unauthorized` cho cả trường hợp sai Email hoặc sai Mật khẩu nhằm ngăn ngừa kỹ thuật rò quét email của Hacker.
* **Chặn tài khoản khóa**: Báo lỗi `400` nếu `is_active == False`.

---

## 🛑 7. FastAPI Dependency Phân Quyền (`app/dependencies/auth.py`)

Tệp này tự động trích xuất Token từ HTTP Header, giải mã và lấy ra User đang gọi API.

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session

from app.db.database import get_session
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User

# Định nghĩa lược đồ OAuth2 đọc Header 'Authorization: Bearer <TOKEN>'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Dependency lấy thông tin User hiện tại dựa vào Token gửi kèm"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin tài khoản",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Giải mã JWT Token
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    # 2. Lấy đối tượng User từ Cơ sở dữ liệu
    user_repo = UserRepository(session)
    user = user_repo.get_by_id(user_id)
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tài khoản đã bị vô hiệu hóa"
        )
        
    return user
```

### 💡 Giải thích tác dụng:
* **`OAuth2PasswordBearer`**: Đọc token từ header `Authorization: Bearer <TOKEN>`.
* Bất kỳ API nào cần bảo vệ chỉ cần thêm tham số: `current_user: User = Depends(get_current_user)`. Nếu không có Token hoặc Token hết hạn, FastAPI sẽ chặn lại và trả về lỗi 401 lập tức.

---

## 🚦 8. Tầng Router Khai Báo API Endpoints (`app/routers/auth.py`)

Khai báo các đường dẫn API tương tác trực tiếp với Client.

```python
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.db.database import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    """Hàm Inject AuthService vào Router"""
    repository = UserRepository(session)
    return AuthService(repository)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """API Đăng ký Tài khoản"""
    return auth_service.register(data)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """API Đăng nhập cấp Token"""
    return auth_service.login(data)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """API Bảo vệ: Lấy thông tin người dùng đang đăng nhập"""
    return current_user
```

---

## 🌐 9. Tích Hợp Router Vào Main Application (`app/main.py`)

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette import status

from app.db.database import create_db_and_tables, test_connection
from app.routers.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Khởi động ứng dụng...")
    test_connection()
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Nexus OMS API",
    version="1.0.0",
)

# Tích hợp Router Authentication vào tiền tố /api/v1
app.include_router(auth_router, prefix="/api/v1")

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Nexus OMS API v1"}
```

---

## 🧪 10. Hướng Dẫn Chạy & Test API Trên Swagger UI

1. **Khởi động server**:
   ```bash
   uvicorn app.main:app --reload
   ```
2. **Truy cập giao diện Swagger UI**:
   Mở trình duyệt truy cập: `http://127.0.0.1:8000/docs`

3. **Quy trình kiểm thử**:
   1. Gọi API `POST /api/v1/auth/register` truyền JSON:
      ```json
      {
        "email": "user@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
      }
      ```
   2. Gọi API `POST /api/v1/auth/login` với thông tin trên. Hệ thống trả về `access_token`.
   3. Nhấp vào nút **Authorize 🔒** ở góc trên bên phải màn hình Swagger, dán chuỗi Token thu được vào ô Value và bấm **Authorize**.
   4. Thử bấm **Execute** API `GET /api/v1/auth/me` để xem thông tin User được truy xuất an toàn.
