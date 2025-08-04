from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Tip, Post_History
from sqlalchemy import func
import random
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()

# Pydantic models for request/response
class TipCreate(BaseModel):
    id: Optional[int] = None
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
    created_at: datetime
    last_posted: Optional[datetime] = None

    class Config:
        from_attributes = True

class HealthCheckResponse(BaseModel):
    status: int
    message: str


@app.get("/", response_model=HealthCheckResponse)
def health_check():
    try: 
        return HealthCheckResponse(status=200, message="Hey there, I'm up and running!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/API/get_random_tip")
def get_tip(db: Session = Depends(get_db)):
    # Determining what day it is
    weekday = datetime.utcnow().weekday()
    category_id = weekday + 1

    # Getting all tip IDs with today category, based on day number(M=1,T=2, W=3...)
    tip_ids = db.query(Tip.id).filter(Tip.category_id == category_id).all()
    tip_ids = [t[0] for t in tip_ids]

    if not tip_ids:
        return {"message": "No tips found for this category"}
    
    # Checking for tips already posted
    posted_ids = db.query(Post_History.tip_id).filter(Post_History.tip_id.in_(tip_ids)).all()
    posted_ids = {p[0] for p in posted_ids}

    # Filter unposted tips
    unposted_ids = list(set(tip_ids) - posted_ids)
    if not unposted_ids:
        return {"message": "All tips in today's category have been posted"}
    
    # Randomly select one
    selected_id = random.choice(unposted_ids)
    selected_tip = db.query(Tip).get(selected_id)

    # Add to post history 
    post_entry = Post_History(
        tip_id=selected_id,
        posted_at=datetime.utcnow(),
        platform="X",
        post_id="",
        engagement_count=0
    )
    db.add(post_entry)

    #s Update Tip's Last_Posted timestampt
    selected_tip.last_posted = datetime.utcnow()
    db.commit()

    return {
        "category_id": selected_tip.category_id,
        "title": selected_tip.title,
        "content": selected_tip.content,
        "code": selected_tip.code_example,
        "hashtags": selected_tip.hashtags,
        "created_at": selected_tip.created_at,
        "last_posted": selected_tip.last_posted
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

