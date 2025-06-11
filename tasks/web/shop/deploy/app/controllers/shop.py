from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.responses import RedirectResponse
from ..config import settings
from ..database import get_db
from .. import models, schemas
from ..limiter import limiter

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

def get_current_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # First try to decode with normal algorithm
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
                    payload = json.loads(payload_str)
                else:
                    return None
            except:
                return None
        
        username = payload.get("sub")
    except Exception:
        return None
    return db.query(models.User).filter_by(username=username).first()

@router.get("/shop")
@limiter.limit("5/second")
def view_shop(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    items = db.query(models.Item).all()
    bought_ids = {i.id for i in user.purchases} if user else set()
    
    # Get error and success messages from query params
    error_param = request.query_params.get("error")
    success_param = request.query_params.get("success")
    
    # Map error codes to messages
    error_messages = {
        "purchase_failed": "Невозможно приобрести",
        "insufficient_funds": "Недостаточно средств"
    }
    
    # Map success codes to messages
    success_messages = {
        "purchased": "Товар успешно приобретен"
    }
    
    error = error_messages.get(error_param)
    success = success_messages.get(success_param)
    
    return templates.TemplateResponse("shop.html", {
        "request": request, 
        "items": items, 
        "user": user, 
        "bought": bought_ids,
        "error": error,
        "success": success
    })

@router.post("/shop/buy")
@limiter.limit("5/second")
def buy_item(request: Request, item_id: int = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login?error=unauthorized", status_code=303)
        return response
    item = db.query(models.Item).get(item_id)
    if not item or item in user.purchases:
        response = RedirectResponse(url="/shop?error=purchase_failed", status_code=303)
        return response
    if user.balance < item.price:
        response = RedirectResponse(url="/shop?error=insufficient_funds", status_code=303)
        return response
    user.balance -= item.price
    user.purchases.append(item)
    db.commit()
    
    response = RedirectResponse(url="/shop?success=purchased", status_code=303)
    return response

@router.post("/shop/return")
@limiter.limit("5/second")
def return_item(request: Request, item_id: int = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login?error=unauthorized", status_code=303)
        return response
    
    # Prevent admin from returning purchases
    if user.username == "admin":
        response = RedirectResponse(url="/profile?error=admin_return_forbidden", status_code=303)
        return response
    
    item = db.query(models.Item).get(item_id)
    if not item:
        response = RedirectResponse(url="/profile?error=item_not_found", status_code=303)
        return response
    
    # Check if user has this item
    if item not in user.purchases:
        response = RedirectResponse(url="/profile?error=item_not_owned", status_code=303)
        return response
    
    # Return item and refund money
    user.balance += item.price
    user.purchases.remove(item)
    db.commit()
    
    response = RedirectResponse(url="/profile?success=item_returned", status_code=303)
    return response
