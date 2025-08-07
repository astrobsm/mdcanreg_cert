import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Path to app.py
app_path = 'app.py'

try:
    # Read the current content of app.py
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Look for the SQLAlchemy initialization part
    start_marker = "# Initialize SQLAlchemy"
    db_init_line = "db = SQLAlchemy(app)"
    
    # If we find the initialization line
    if db_init_line in content:
        # Add code to refresh metadata after initialization
        updated_content = content.replace(
            db_init_line,
            f"{db_init_line}\n\n# Ensure SQLAlchemy metadata is up-to-date with the actual database schema\nwith app.app_context():\n    try:\n        db.reflect()\n        print('✅ SQLAlchemy metadata refreshed')\n    except Exception as e:\n        print(f'❌ Error refreshing metadata: {{e}}')"
        )
        
        # Write the updated content back to app.py
        with open(app_path, 'w') as f:
            f.write(updated_content)
        
        print("✅ Added metadata refresh to app.py")
    else:
        print("❌ Could not find SQLAlchemy initialization in app.py")
    
except Exception as e:
    print(f"❌ Error updating app.py: {e}")
    sys.exit(1)
