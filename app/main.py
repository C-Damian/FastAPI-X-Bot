from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Tip
from sqlalchemy import func
import random
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Pydantic models for request/response
class TipCreate(BaseModel):
    category_id: int
    title: str
    content: str
    code_example: Optional[str] = None
    hashtags: Optional[str] = "#DailyTechTip #Coding"
    is_ai_generated: bool = False

class TipResponse(BaseModel):
    id: int
    category_id: int
    title: str
    content: str
    code_example: Optional[str]
    hashtags: Optional[str]
    is_ai_generated: bool

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/API/get_random_tip")
def get_tip(db: Session = Depends(get_db)):
    tip = db.query(Tip).order_by(func.random()).first()
    if not tip:
        return {"message": "No tip found"}
    return {
        "category_id": tip.category_id,
        "title": tip.title,
        "content": tip.content,
        "code": tip.code_example,
        "hashtags": tip.hashtags,
        "created_at": tip.created_at,
        "last_posted": tip.last_posted
    }

@app.post("/API/add_new_tip", response_model=TipResponse)
def create_tip(tip: TipCreate, db: Session = Depends(get_db)):
    """Create a new tech tip"""
    try:
        db_tip = Tip(
            category_id=tip.category_id,
            title=tip.title,
            content=tip.content,
            code_example=tip.code_example,
            hashtags=tip.hashtags,
            is_ai_generated=tip.is_ai_generated
        )
        db.add(db_tip)
        db.commit()
        db.refresh(db_tip)
        return db_tip
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create tip: {str(e)}")

@app.delete("/API/delete_tips/{tip_id}")
def delete_tip(tip_id: int, db: Session = Depends(get_db)):
    """Delete a tech tip by ID"""
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    
    try:
        db.delete(tip)
        db.commit()
        return {"message": f"Tip {tip_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to delete tip: {str(e)}")

@app.get("/API/get_all_tips", response_model=list[TipResponse])
def get_all_tips(db: Session = Depends(get_db)):
    """Get all tech tips"""
    tips = db.query(Tip).all()
    return tips

