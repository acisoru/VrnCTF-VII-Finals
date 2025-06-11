from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine, SessionLocal, get_db
from .controllers import auth, shop, user
from .seed import seed_items, seed_admin
from . import models
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .limiter import limiter

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed initial data
db = SessionLocal()
try:
    seed_items(db)
    seed_admin(db)
finally:
    db.close()

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(shop.router)
app.include_router(user.router)

templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@app.get("/")
@limiter.limit("5/second")
def home(request: Request, db: Session = Depends(get_db)):
    from .controllers.shop import get_current_user
    
    user = get_current_user(request, db)
    items = db.query(models.Item).all()
    bought_ids = {i.id for i in user.purchases} if user else set()
    
    return templates.TemplateResponse("shop.html", {
        "request": request, 
        "items": items, 
        "user": user, 
        "bought": bought_ids
    })
