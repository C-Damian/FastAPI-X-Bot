#!/usr/bin/env python3
"""
Database setup script for Daily Tech Tip Bot
Run this after creating the database to set up tables and seed data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'tech_tip_bot',
    'user': 'postgres',  # Change if needed
    'password': ''  # Add password if you set one
}

def create_tables(cursor):
    """Create the database tables"""
    
    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Tips table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id SERIAL PRIMARY KEY,
            category_id INTEGER REFERENCES categories(id),
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            code_example TEXT,
            hashtags VARCHAR(200) DEFAULT '#DailyTechTip #Coding',
            is_ai_generated BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_posted TIMESTAMP
        );
    """)
    
    # Post history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_history (
            id SERIAL PRIMARY KEY,
            tip_id INTEGER REFERENCES tips(id),
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            platform VARCHAR(20) DEFAULT 'twitter',
            post_id VARCHAR(100),
            engagement_count INTEGER DEFAULT 0
        );
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tips_category ON tips(category_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tips_last_posted ON tips(last_posted);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_history_posted_at ON post_history(posted_at);")
    
    print("✅ Tables created successfully!")

def seed_categories(cursor):
    """Insert category data"""
    categories = [
        ('Python', 'Python programming tips and tricks'),
        ('JavaScript', 'JavaScript and web development tips'),
        ('DevOps', 'DevOps, deployment, and infrastructure tips'),
        ('Git', 'Version control and Git workflow tips'),
        ('Performance', 'Code optimization and performance tips'),
        ('Security', 'Security best practices and tips'),
        ('Debugging', 'Debugging techniques and tools'),
        ('APIs', 'API development and integration tips')
    ]
    
    for name, description in categories:
        cursor.execute("""
            INSERT INTO categories (name, description) 
            VALUES (%s, %s) 
            ON CONFLICT (name) DO NOTHING;
        """, (name, description))
    
    print("✅ Categories seeded successfully!")

def seed_tips(cursor):
    """Insert tip data"""
    
    # Get category IDs
    cursor.execute("SELECT id, name FROM categories;")
    categories = {row['name']: row['id'] for row in cursor.fetchall()}
    
    tips = [
        # Python tips
        (categories['Python'], 'Use enumerate() for cleaner loops', 
         'Instead of manually tracking indices, use enumerate() to get both index and value in loops.',
         'for i, item in enumerate(my_list):\n    print(f"{i}: {item}")',
         '#Python #Programming #CleanCode'),
        
        (categories['Python'], 'Dictionary get() method with defaults',
         'Use dict.get() with a default value instead of checking if key exists.',
         'count = my_dict.get("key", 0)\n# Instead of:\n# count = my_dict["key"] if "key" in my_dict else 0',
         '#Python #Tips #DictTips'),
        
        (categories['Python'], 'List comprehensions for filtering',
         'Create filtered lists in one line with list comprehensions.',
         'evens = [x for x in numbers if x % 2 == 0]\n# Instead of a for loop with append',
         '#Python #ListComprehension #CleanCode'),
         
        (categories['Python'], 'Use pathlib for file operations',
         'pathlib is more readable and cross-platform than os.path.',
         'from pathlib import Path\nfile_path = Path("data") / "file.txt"\nif file_path.exists():\n    content = file_path.read_text()',
         '#Python #FileHandling #PathLib'),
        
        # JavaScript tips
        (categories['JavaScript'], 'Use optional chaining (?.) safely',
         'Access nested object properties without worrying about undefined.',
         'const city = user?.profile?.address?.city;\n// No more "Cannot read property of undefined" errors',
         '#JavaScript #ES2020 #SafeAccess'),
        
        (categories['JavaScript'], 'Destructuring with default values',
         'Extract values from objects/arrays with fallback defaults.',
         'const {name = "Anonymous", age = 0} = user;\nconst [first, second = "default"] = array;',
         '#JavaScript #Destructuring #ES6'),
        
        (categories['JavaScript'], 'Use Array.includes() for multiple conditions',
         'Check if a value matches any of several options cleanly.',
         'if (["admin", "moderator", "owner"].includes(user.role)) {\n    // User has elevated permissions\n}',
         '#JavaScript #Arrays #CleanCode'),
        
        # DevOps tips
        (categories['DevOps'], 'Use Docker multi-stage builds',
         'Reduce image size by using multi-stage builds to exclude build dependencies.',
         'FROM node:16 AS builder\nCOPY . .\nRUN npm ci && npm run build\n\nFROM node:16-alpine\nCOPY --from=builder /app/dist ./dist\nCMD ["node", "dist/server.js"]',
         '#Docker #DevOps #Optimization'),
        
        (categories['DevOps'], 'Health checks in Docker containers',
         'Add health checks to monitor container status properly.',
         'HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \\\n  CMD curl -f http://localhost:3000/health || exit 1',
         '#Docker #HealthCheck #Monitoring'),
        
        # Git tips
        (categories['Git'], 'Use conventional commit messages',
         'Structure commit messages for better changelog generation.',
         'feat: add user authentication\nfix: resolve memory leak in parser\ndocs: update API documentation\nrefactor: simplify user service logic',
         '#Git #CommitMessages #Changelog'),
        
        (categories['Git'], 'Interactive rebase for clean history',
         'Use interactive rebase to squash, reorder, or edit commits.',
         'git rebase -i HEAD~3\n# Then squash or fixup commits for cleaner history',
         '#Git #Rebase #CleanHistory'),
        
        # Security tips  
        (categories['Security'], 'Never store secrets in code',
         'Use environment variables or secret management systems for sensitive data.',
         '# ❌ Bad\nAPI_KEY = "secret-key-123"\n\n# ✅ Good\nimport os\nAPI_KEY = os.getenv("API_KEY")\nif not API_KEY:\n    raise ValueError("API_KEY environment variable required")',
         '#Security #Secrets #EnvironmentVariables'),
        
        (categories['Security'], 'Validate all input data',
         'Always validate and sanitize user input to prevent injection attacks.',
         '# Python with Pydantic\nfrom pydantic import BaseModel, EmailStr\n\nclass UserInput(BaseModel):\n    email: EmailStr\n    age: int = Field(ge=0, le=150)\n    name: str = Field(min_length=1, max_length=100)',
         '#Security #InputValidation #DataValidation'),
        
        # Performance tips
        (categories['Performance'], 'Use database indexes strategically',
         'Add indexes on columns used in WHERE, ORDER BY, and JOIN clauses.',
         'CREATE INDEX idx_user_email ON users(email);\nCREATE INDEX idx_post_created_at ON posts(created_at DESC);',
         '#Database #Performance #Indexing'),
        
        (categories['Performance'], 'Cache expensive computations',
         'Store results of expensive operations to avoid recomputation.',
         '# Python with functools\nfrom functools import lru_cache\n\n@lru_cache(maxsize=128)\ndef expensive_function(param):\n    # Expensive computation here\n    return result',
         '#Caching #Performance #Optimization'),
        
        # API tips
        (categories['APIs'], 'Use proper HTTP status codes',
         'Return appropriate status codes for different API responses.',
         '200 OK - Success\n201 Created - Resource created\n400 Bad Request - Invalid input\n401 Unauthorized - Authentication required\n404 Not Found - Resource not found\n500 Internal Server Error - Server error',
         '#API #HTTPStatusCodes #RESTful'),
        
        (categories['APIs'], 'Version your APIs from the start',
         'Include versioning in your API design to handle future changes.',
         '# URL versioning\nGET /api/v1/users\nGET /api/v2/users\n\n# Header versioning\nGET /api/users\nAccept: application/vnd.myapi.v1+json',
         '#API #Versioning #BackwardCompatibility'),
        
        # Debugging tips
        (categories['Debugging'], 'Use debugger instead of print statements',
         'Set breakpoints and inspect variables with a proper debugger.',
         '# Python\nimport pdb; pdb.set_trace()\n\n# JavaScript (browser)\ndebugger;\n\n# Node.js\nnode --inspect-brk app.js',
         '#Debugging #Debugger #DeveloperTools'),
        
        (categories['Debugging'], 'Log with context and timestamps',
         'Include relevant context in your log messages.',
         'import logging\n\nlogger = logging.getLogger(__name__)\nlogger.info(\n    "User login attempt", \n    extra={"user_id": user.id, "ip": request.remote_addr}\n)',
         '#Debugging #Logging #Context')
    ]
    
    for category_id, title, content, code_example, hashtags in tips:
        cursor.execute("""
            INSERT INTO tips (category_id, title, content, code_example, hashtags)
            VALUES (%s, %s, %s, %s, %s);
        """, (category_id, title, content, code_example, hashtags))
    
    print(f"✅ {len(tips)} tips seeded successfully!")

def main():
    """Main setup function"""
    try:
        # Connect to PostgreSQL
        print("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("📊 Setting up database schema...")
        create_tables(cursor)
        
        print("🌱 Seeding categories...")
        seed_categories(cursor)
        
        print("💡 Seeding tips...")
        seed_tips(cursor)
        
        # Show summary
        cursor.execute("SELECT COUNT(*) as count FROM categories;")
        category_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tips;")
        tip_count = cursor.fetchone()['count']
        
        print(f"\n🎉 Database setup complete!")
        print(f"📁 Categories: {category_count}")
        print(f"💡 Tips: {tip_count}")
        print(f"🔗 Database: {DB_CONFIG['database']}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running (check Postgres.app)")
        print("2. Create the database first: createdb tech_tip_bot")
        print("3. Check your connection settings in DB_CONFIG")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()