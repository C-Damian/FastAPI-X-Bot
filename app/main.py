from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Tip, Post_History
from sqlalchemy import func
import random
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from generateTip import generate_tip
from createTweet import post_tweet
import os

def get_current_category_id():
    """Get the category ID for the current day of the week"""
    weekday = datetime.utcnow().weekday()
    return weekday + 1

def get_unposted_tips_for_category(db: Session, category_id: int):
    """
    Get all unposted tips for a specific category.
    Returns list of Tip objects or None if no tips available.
    """
    # Getting all tip IDs with today category
    tip_ids = db.query(Tip.id).filter(Tip.category_id == category_id).all()
    tip_ids = [t[0] for t in tip_ids]

    if not tip_ids:
        return None
    
    # Checking for tips already posted
    posted_ids = db.query(Post_History.tip_id).filter(Post_History.tip_id.in_(tip_ids)).all()
    posted_ids = {p[0] for p in posted_ids}

    # Filter unposted tips
    unposted_ids = list(set(tip_ids) - posted_ids)
    if not unposted_ids:
        return None
    
    # Get the actual tip objects
    unposted_tips = db.query(Tip).filter(Tip.id.in_(unposted_ids)).all()
    return unposted_tips

def select_random_tip(tips):
    """Select a random tip from a list of tips"""
    if not tips:
        return None
    return random.choice(tips)

def mark_tip_as_posted(db: Session, tip_id: int, tweet_id: str = ""):
    """
    Mark a tip as posted in the database.
    Creates post history entry and updates tip's last_posted timestamp.
    """
    # Add to post history 
    post_entry = Post_History(
        tip_id=tip_id,
        posted_at=datetime.utcnow(),
        platform="X",
        post_id=tweet_id,
        engagement_count=0
    )
    db.add(post_entry)

    # Update Tip's Last_Posted timestamp
    tip = db.query(Tip).get(tip_id)
    tip.last_posted = datetime.utcnow()
    db.commit()

def create_tip_internal(db: Session, category_id: int = None):
    """
    Internal function to create a new tip in the database.
    If category_id is None, uses current day's category.
    """
    if category_id is None:
        category_id = get_current_category_id()
    
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

def get_tip_for_posting(db: Session):
    """
    Get a tip for posting, post it to Twitter, and mark it as posted.
    Returns the tip data as a dictionary or None if no tips available.
    """
    category_id = get_current_category_id()
    
    # Get unposted tips for today's category
    unposted_tips = get_unposted_tips_for_category(db, category_id)
    
    if not unposted_tips:
        return None
    
    # Select a random tip
    selected_tip = select_random_tip(unposted_tips)
    
    # Format tweet content: title<br>content<br>code<br>hashtags
    tweet_content = selected_tip.title
    
    if selected_tip.content:
        tweet_content += f"\n\n{selected_tip.content}"
    
    if selected_tip.code_example:
        tweet_content += f"\n\n{selected_tip.code_example}"
    
    if selected_tip.hashtags:
        tweet_content += f"\n\n{selected_tip.hashtags}"
    
    # Post to Twitter
    success, tweet_id = post_tweet(tweet_content)
    
    # Mark it as posted (include the tweet_id if successful)
    mark_tip_as_posted(db, selected_tip.id, tweet_id if success else "")
    
    # Generate a new tip to replace the one we just used
    try:
        create_tip_internal(db, category_id)
    except Exception as e:
        print(f"Failed to generate new tip: {str(e)}")
    
    # Return tip data as dictionary
    return {
        "category_id": selected_tip.category_id,
        "title": selected_tip.title,
        "content": selected_tip.content,
        "code": selected_tip.code_example,
        "hashtags": selected_tip.hashtags,
        "created_at": selected_tip.created_at,
        "last_posted": selected_tip.last_posted,
        "tweet_posted": success,
        "tweet_id": tweet_id if success else None
    }

def delete_tip_internal(db: Session, tip_id: int):
    """
    Internal function to delete a tip by ID.
    Returns True if successful, False if tip not found.
    """
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        return False
    
    try:
        db.delete(tip)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e

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
    """Get a random tip for posting"""
    tip_data = get_tip_for_posting(db)
    
    if not tip_data:
        return {"message": "No tips available for posting today"}
    
    return tip_data

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
    try:
        success = delete_tip_internal(db, tip_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tip not found")
        return {"message": f"Tip {tip_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete tip: {str(e)}")

@app.get("/API/get_all_tips", response_model=list[TipResponse])
def get_all_tips(db: Session = Depends(get_db)):
    """Get all tech tips"""
    tips = db.query(Tip).all()
    return tips

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
