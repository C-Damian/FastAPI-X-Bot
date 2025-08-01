from fastapi import Depends
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

DB_URL = "postgresql://damian:postgresql@localhost:5432/tech_tip_bot"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()