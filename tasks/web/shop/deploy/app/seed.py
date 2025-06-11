from sqlalchemy.orm import Session
from .models import Item, User
from .controllers.auth import get_password_hash

# Define 5 blueprint items to add to the database
blueprint_items = [
    {
        "title": "Базовый чертеж",
        "image": "/static/images/blueprint1.jpg",
        "description": "Базовый чертеж для начинающих",
        "price": 50
    },
    {
        "title": "Продвинутый чертеж",
        "image": "/static/images/blueprint2.jpg",
        "description": "Более сложный дизайн для опытных пользователей",
        "price": 100
    },
    {
        "title": "Премиум чертеж",
        "image": "/static/images/blueprint3.jpg",
        "description": "Высококачественный чертеж с подробными спецификациями",
        "price": 150
    },
    {
        "title": "Особый чертеж",
        "image": "/static/images/blueprint4.jpg",
        "description": "Ограниченная серия чертежей с уникальными функциями",
        "price": 200
    },
    {
        "title": "Чертеж Гото Предестинация",
        "image": "/static/images/blueprint5.jpg",
        "description": "vrnctf{jw7_blu3pr1n7_5h0p}",
        "price": 999
    }
]

def seed_items(db: Session):
    """Seed the database with blueprint items if they don't already exist."""
    # Check if we already have items in the database
    existing_count = db.query(Item).count()
    
    if existing_count == 0:
        print("Seeding database with initial blueprint items...")
        for item_data in blueprint_items:
            item = Item(**item_data)
            db.add(item)
        db.commit()
        print(f"Added {len(blueprint_items)} blueprint items to database")
    else:
        print(f"Database already contains {existing_count} items. Skipping seed.")

def seed_admin(db: Session):
    """Create admin user with all items purchased if it doesn't exist."""
    admin = db.query(User).filter_by(username="admin").first()
    
    if not admin:
        print("Creating admin user...")
        # Create admin user with 9999 balance
        hashed_password = get_password_hash("a4TUtr97ZbVxeQjlzQn7QrE4nNpkfpbkjc86h1EW")
        admin = User(
            username="admin", 
            hashed_password=hashed_password,
            balance=9999
        )
        db.add(admin)
        db.commit()
        
        # Add all items to admin's purchases
        items = db.query(Item).all()
        admin.purchases.extend(items)
        db.commit()
        print("Admin user created with all items purchased")
    else:
        print("Admin user already exists. Skipping admin seed.") 