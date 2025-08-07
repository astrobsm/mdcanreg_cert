import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL environment variable not set")
    sys.exit(1)

# Create a Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

try:
    # Test connection
    with app.app_context():
        # Execute a simple query to test connection
        result = db.session.execute(text('SELECT 1'))
        print("✅ Database connection test successful")
        
        # Refresh metadata - this will reload table definitions from the database
        db.metadata.reflect(bind=db.engine)
        print("✅ Metadata refreshed successfully")
        
        # Check if the participants table exists
        if 'participants' in db.metadata.tables:
            print("✅ Participants table exists in metadata")
            
            # Check columns in participants table
            participants_table = db.metadata.tables['participants']
            columns = [column.name for column in participants_table.columns]
            print(f"Columns in participants table: {', '.join(columns)}")
            
            # Check for specific columns
            required_columns = [
                'first_attendance_date', 
                'last_attendance_date', 
                'materials_provided', 
                'materials_provided_date', 
                'materials_provided_by'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {', '.join(missing_columns)}")
            else:
                print("✅ All required columns exist")
        else:
            print("❌ Participants table not found in metadata")
        
except Exception as e:
    print(f"❌ Error checking database: {e}")
    sys.exit(1)
