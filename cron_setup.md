# Cron Job Setup Guide

## Setting up Automated Daily Posting

### 1. Environment Variables
Add these to your `.env` file:
```
GEMINI_KEY=your_gemini_api_key
TWITTER_AUTH_HEADER=your_twitter_auth_header
TWITTER_COOKIE=your_twitter_cookie
```

### 2. Test the Script Manually
First, test that everything works:
```bash
cd app
python automated_poster.py
```

### 3. Set up Cron Job

#### Option A: Using crontab (Linux/Mac)
```bash
# Open crontab editor
crontab -e

# Add this line to post daily at 9 AM
0 9 * * * cd /path/to/your/project/app && python automated_poster.py >> /path/to/your/project/logs/cron.log 2>&1
```

#### Option B: Using Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily at 9 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `automated_poster.py`
7. Start in: `C:\path\to\your\project\app`

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cron Job      │───▶│ automated_poster │───▶│   Twitter API   │
│   (Daily 9 AM)  │    │      .py         │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   main.py        │
                       │   (Internal      │
                       │    Functions)    │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Database       │
                       │   (PostgreSQL)   │
                       └──────────────────┘
```

## Benefits of This Approach

✅ **No code duplication** - Uses same functions as API endpoints
✅ **Single source of truth** - All logic in main.py
✅ **Easy to maintain** - Change logic in one place
✅ **Cron job friendly** - Can be scheduled easily  
✅ **Self-contained** - Doesn't need the FastAPI server running
✅ **Error handling** - Proper logging and error management
✅ **Automatic replenishment** - Generates new tips after posting

## Internal Functions Available

- `get_current_category_id()` - Get today's category
- `get_unposted_tips_for_category()` - Get available tips
- `select_random_tip()` - Pick a random tip
- `mark_tip_as_posted()` - Mark tip as posted
- `create_tip_internal()` - Generate new tip
- `get_tip_for_posting()` - Main function for posting
- `delete_tip_internal()` - Delete tips

## Next Steps

1. Set up proper Twitter API authentication
2. Add more robust error handling
3. Implement engagement tracking
4. Add analytics dashboard 