# FastAPI X Bot 🤖

A smart Twitter/X bot that posts daily tech tips using FastAPI and AI. Currently in development with plans to integrate Hugging Face for AI-generated content and Tweepy for social media automation.

## 🚀 Tech Stack

**Backend:**
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM for database operations
- **PostgreSQL** - Robust relational database
- **Scheduled tip selection logic** - Automatically picks one unposted tip per day from a rotating category
- **Pydantic** - Data validation using Python type annotations

**Future Integrations:**
- **Hugging Face** - AI model integration for content generation
- **Tweepy** - Twitter/X API wrapper for automated posting

## 🛠️ Current Features

- **CRUD Operations** for tech tips
- **Random tip generation** for daily posts
- **Rotating category-based tip selection** with logic to avoid reposting the same tip
- **Database management** with PostgreSQL
- **RESTful API** with automatic documentation

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/API/get_random_tip` | Get a random tech tip |
| `GET` | `/API/get_all_tips` | Get all tech tips |
| `POST` | `/API/add_new_tip` | Create a new tech tip |
| `DELETE` | `/API/delete_tips/{tip_id}` | Delete a tip by ID |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd FastAPI-X-Bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   python setup_db.py
   ```

5. **Run the application**
   ```bash
   cd app
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## 📊 Database Schema

The bot uses a PostgreSQL database with the following main tables:
- **categories** - Tech tip categories (Python, JavaScript, DevOps, etc.)
- **tips** - Individual tech tips with content and metadata
- **post_history** - Tracks which tips have been posted, including timestamp, platform, and engagement metrics; used to ensure unique daily tips

## 🔮 Future Roadmap

- [ ] **AI Integration** - Hugging Face models for generating tech tips
- [ ] **Social Media Automation** - Tweepy integration for automated X posting
- [ ] **Scheduling System** - Automated daily posting at optimal times
- [ ] **Analytics Dashboard** - Track engagement and performance
- [ ] **Content Curation** - Smart filtering and quality control

## 🤝 Contributing

This project is in active development. Feel free to contribute by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests

---
