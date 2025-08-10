# FastAPI X Bot 🤖

An automated Twitter/X bot that posts daily tech tips using FastAPI and AI. Deployed on Render with automatic content generation and posting via Google's Gemini API and Tweepy.

## How It Works

The main endpoint `get_random_tip` handles the entire automation flow:

```mermaid
graph TD
    A[Daily Trigger] --> B[get_random_tip Endpoint]
    B --> C{Check for Unposted Tips}
    C -->|Yes| D[Select Random Tip for Post]
    C -->|Automatically Replenish Tip (1 out 1 in)| E[Call Gemini API]
    E --> F[Generate New Tip]
    F --> G[Store in Database]
    G --> D
    D --> H[Post to X via Tweepy]
    H --> I[Mark as Posted]
    I --> J[Update Post History]
```

## Tech Stack

**Backend:**
- **FastAPI** - Web framework and API
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation

**AI & Automation:**
- **Google Gemini API** - AI tip generation
- **Tweepy** - Twitter/X API integration
- **Render** - Cloud deployment
- **Cron jobs** - Scheduled posting

## Features

- **Automated posting** - Daily tech tips without manual intervention
- **AI content generation** - New tips created when supply runs low
- **Duplicate prevention** - Tracks posted tips to avoid repeats
- **Category rotation** - Ensures diverse content across tech topics
- **Self-sustaining pipeline** - Maintains content supply automatically

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/API/get_random_tip` | **Main automation endpoint** - selects tip, generates new content if needed, posts to X |
| `GET` | `/API/get_all_tips` | Get all tech tips |
| `POST` | `/API/add_new_tip` | Create a new tech tip | Generate Tips on Demand
| `DELETE` | `/API/delete_tips/{tip_id}` | Delete a tip by ID | If ever needed

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Setup

1. **Clone and setup environment**
   ```bash
   git clone <your-repo-url>
   cd FastAPI-X-Bot
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment variables (.env file)**
   ```bash
   GEMINI_KEY=your_gemini_api_key_here
   TWITTER_AUTH_HEADER=your_twitter_auth_header
   TWITTER_COOKIE=your_twitter_cookie
   DATABASE_URL=your_postgresql_url
   ```

3. **Initialize database and run**
   ```bash
   python setup_db.py
   cd app
   uvicorn main:app --reload
   ```

4. **Access API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## Database Schema

- **`categories`** - Tech tip categories (Python, JavaScript, DevOps, etc.)
- **`tips`** - Individual tech tips with content and metadata
- **`posted_tips`** - Posting history and duplicate prevention

## Deployment

Currently deployed on **Render** with automatic daily posting enabled.

## Contributing
This is a personal portfolio project, but if you'd like you can:

- Report bugs or suggest features
- Submit pull requests
- Help improve documentation

---