from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')

engine = create_engine(DB_URL)

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP)

    # Relationship
    tips = relationship("Tip", back_populates="category")

class Tip(Base):
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    code_example = Column(Text)
    hashtags = Column(String(200))
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP)
    last_posted = Column(TIMESTAMP)

    # Relationship
    category = relationship("Category", back_populates="tips")
    post_history = relationship("Post_History", back_populates="tip")
    
class Post_History(Base):
    __tablename__ = "post_history"

    id = Column(Integer, primary_key=True, index=True)
    tip_id = Column(Integer, ForeignKey("tips.id"))
    posted_at = Column(TIMESTAMP)
    platform = Column(String(200))
    post_id = Column(String(200))
    engagement_count = Column(Integer)

    # Relationship
    tip = relationship("Tip", back_populates="post_history")


Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()
Base.metadata.create_all(engine)

category_seed = [
    Category(name="Python", description="Tips related to Python programming.", created_at=datetime.now(timezone.utc)),
    Category(name="JavaScript", description="Tips related to JavaScript programming.", created_at=datetime.now(timezone.utc)),
    Category(name="DevOps", description="Tips related to DevOps practices.", created_at=datetime.now(timezone.utc)),
    Category(name="Git", description="Tips related to Git version control.", created_at=datetime.now(timezone.utc)),
    Category(name="Performance", description="Tips related to Performance optimization.", created_at=datetime.now(timezone.utc)),
    Category(name="Security", description="Tips related to Security best practices.", created_at=datetime.now(timezone.utc)),
    Category(name="APIs", description="Tips related to API development.", created_at=datetime.now(timezone.utc)),
]

session.add_all(category_seed)
session.commit()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()