from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..database import get_db
from ..config import settings
from .. import models
from ..limiter import limiter

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_current_user(request: Request, db: Session):
    from jose import jwt, JWTError
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # First try to decode with normal algorithm
        try:
            data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            # If normal decoding fails, try with none algorithm
            # Manually split the token to verify all three parts exist
            token_parts = token.split('.')
            if len(token_parts) != 3:
                return None
                
            # Manually decode the payload without verification
            import base64
            import json
            
            # Parse the header to check if alg is none
            try:
                header = json.loads(base64.urlsafe_b64decode(token_parts[0] + '==').decode('utf-8'))
                if header.get('alg') == 'none':
                    # Decode payload without verification if alg is none
                    payload_str = base64.urlsafe_b64decode(token_parts[1] + '==').decode('utf-8')
                    data = json.loads(payload_str)
                else:
                    return None
            except:
                return None
                
        username = data.get("sub")
    except Exception:
        return None
    return db.query(models.User).filter_by(username=username).first()

@router.get("/profile")
@limiter.limit("5/second")
def profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?error=unauthorized", status_code=303)
    
    # Get error and success messages from query params
    error_param = request.query_params.get("error")
    success_param = request.query_params.get("success")
    
    # Map error codes to messages
    error_messages = {
        "admin_return_forbidden": "Администратор не может возвращать покупки",
        "item_not_found": "Товар не найден",
        "item_not_owned": "У вас нет этого предмета"
    }
    
    # Map success codes to messages
    success_messages = {
        "item_returned": "Возврат товара выполнен успешно. Средства зачислены на ваш баланс",
        "password_changed": "Пароль успешно изменен"
    }
    
    error = error_messages.get(error_param)
    success = success_messages.get(success_param)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "purchases": user.purchases,
        "error": error,
        "success": success
    })

@router.get("/change-password")
@limiter.limit("5/second")
def change_password_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?error=unauthorized", status_code=303)
    
    # Get error from query params
    error = request.query_params.get("error")
    error_messages = {
        "invalid_credentials": "Неверные учетные данные",
        "admin_forbidden": "Невозможно изменить пароль для учетной записи admin"
    }
    error_msg = error_messages.get(error)
    
    return templates.TemplateResponse("change_password.html", {
        "request": request, 
        "user": user,
        "error": error_msg
    })

@router.post("/change-password")
@limiter.limit("5/second")
def change_password(request: Request,
                    old_password: str = Form(...),
                    new_password: str = Form(...),
                    db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?error=unauthorized", status_code=303)
    
    # Prevent changing admin password
    if user.username == "admin":
        return RedirectResponse(url="/change-password?error=admin_forbidden", status_code=303)
        
    if not pwd_context.verify(old_password, user.hashed_password):
        return RedirectResponse(url="/change-password?error=invalid_credentials", status_code=303)
    
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    
    return RedirectResponse(url="/profile?success=password_changed", status_code=303)

@router.post("/delete-account")
@limiter.limit("5/second")
def delete_account(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Prevent deleting admin account
    if user.username == "admin":
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "purchases": user.purchases,
            "error": "Невозможно удалить учетную запись admin"
        }, status_code=403)
    
    # Remove user purchases associations
    user.purchases = []
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    # Create a response that will redirect to login page
    response = RedirectResponse(url="/login", status_code=302)
    
    # Clear the authentication cookie
    response.delete_cookie(key="access_token")
    
    return response
