from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Tip, Post_History
from sqlalchemy import func
import random
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from generateTip import generate_tip

def create_tip_internal(db: Session, category_id: int = None):
    """
    Internal function to create a new tip in the database.
    If category_id is None, uses current day's category.
    """
    if category_id is None:
        weekday = datetime.utcnow().weekday()
        category_id = weekday + 1
    
    response = generate_tip(category_id)
    
    db_tip = Tip(
        category_id=response['category_id'],
        title=response['title'],
        content=response['content'],
        code_example=response['code_example'],
        hashtags=response['hashtags'],
        is_ai_generated=response['is_ai_generated'],
        created_at=response['created_at']
    )
    db.add(db_tip)
    db.commit()
    db.refresh(db_tip)
    return db_tip

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
    created_at: datetime

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

    # Update Tip's Last_Posted timestamp
    selected_tip.last_posted = datetime.utcnow()
    db.commit()

    # Generate a new tip to replace the one we just used
    try:
        create_tip_internal(db, category_id)
    except Exception as e:
        # If generating new tip fails, don't break the main function
        print(f"Failed to generate new tip: {str(e)}")

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
        # Use the internal function to create the tip
        db_tip = create_tip_internal(db)
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

