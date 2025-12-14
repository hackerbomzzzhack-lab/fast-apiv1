from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker



# -------------------------
# Database setup (SQLite)
# -------------------------
DATABASE_URL = "sqlite:///./local.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# -------------------------
# Database Model
# -------------------------
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# -------------------------
# Pydantic Schemas
# -------------------------
class ItemCreate(BaseModel):
    name: str
    description: str

class ItemResponse(ItemCreate):
    id: int

    class Config:
        orm_mode = True

# -------------------------
# FastAPI App
# -------------------------
app = FastAPI()
mcp = FastApiMCP(app)

# -------------------------
# Root endpoint
# -------------------------
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel!"}

# -------------------------
# CPU-bound task example
# -------------------------
@app.get("/cpu-task")
def run_cpu_task():
    import time
    time.sleep(0.5)
    return {"result": "CPU task finished"}

# -------------------------
# CRUD Endpoints
# -------------------------

# Create item
@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate):
    db = SessionLocal()
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

# Read all items
@app.get("/items", response_model=List[ItemResponse])
def get_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items

# Read single item
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Update item
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, updated_item: ItemCreate):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = updated_item.name
    item.description = updated_item.description
    db.commit()
    db.refresh(item)
    db.close()
    return item

# Delete item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    db.close()
    return {"message": "Item deleted successfully"}



mcp.mount()

