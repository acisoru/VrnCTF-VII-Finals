from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import settings
from ..database import get_db
from .. import models, schemas
from ..limiter import limiter

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(pwd):
    return pwd_context.hash(pwd)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.get("/register")
@limiter.limit("5/second")
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
@limiter.limit("5/second")
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()
    if user:
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "error": "Имя пользователя уже зарегистрировано"
            },
            status_code=400
        )
    hashed = get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed)
    db.add(new_user); db.commit(); db.refresh(new_user)
    response = RedirectResponse(url="/login?success=registered", status_code=status.HTTP_303_SEE_OTHER)
    return response

@router.get("/login")
@limiter.limit("5/second")
def login_form(request: Request):
    success = request.query_params.get("success")
    error = request.query_params.get("error")
    
    # Map error codes to messages
    error_messages = {
        "unauthorized": "Для доступа к этой странице необходимо авторизоваться"
    }
    
    # Map success codes to messages
    success_messages = {
        "registered": "Регистрация успешна! Теперь вы можете войти."
    }
    
    success_msg = success_messages.get(success)
    error_msg = error_messages.get(error)
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "success": success_msg,
        "error": error_msg
    })

@router.post("/login")
@limiter.limit("5/second")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "error": "Неверные учетные данные"
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    token = create_access_token({"sub": user.username})
    
    # Get items for shop page
    items = db.query(models.Item).all()
    bought_ids = {i.id for i in user.purchases}
    
    # Render shop page with success message
    response = templates.TemplateResponse("shop.html", {
        "request": request,
        "items": items,
        "user": user,
        "bought": bought_ids,
        "success": "Авторизация успешна. Добро пожаловать!"
    })
    
    # Set cookie with token
    response.set_cookie("access_token", token, httponly=True)
    return response

@router.get("/logout")
@limiter.limit("5/second")
def logout(request: Request, db: Session = Depends(get_db)):
    # Get items for shop page
    items = db.query(models.Item).all()
    
    # Render shop page with success message
    response = templates.TemplateResponse("shop.html", {
        "request": request,
        "items": items,
        "user": None,
        "bought": set(),
        "success": "Вы успешно вышли из системы"
    })
    
    # Delete token cookie
    response.delete_cookie("access_token")
    return response
