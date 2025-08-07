import os
import sys

def update_app_py():
    # Path to app.py
    app_py_path = 'app.py'
    
    # Check if file exists
    if not os.path.exists(app_py_path):
        print(f"Error: {app_py_path} not found.")
        return False
    
    # Read the file content
    with open(app_py_path, 'r') as file:
        content = file.read()
    
    # Replace the database URL
    old_db_url = "postgresql://postgres:natiss_natiss@localhost/bdmcertificate_db"
    new_db_url = "postgresql://postgres:natiss_natiss@localhost/mdcan042_db"
    
    # Update the content
    updated_content = content.replace(old_db_url, new_db_url)
    
    # Also update the variable if it's using an environment variable
    old_db_url_line = "DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:natiss_natiss@localhost/bdmcertificate_db')"
    new_db_url_line = "DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:natiss_natiss@localhost/mdcan042_db')"
    
    updated_content = updated_content.replace(old_db_url_line, new_db_url_line)
    
    # Write the updated content back to the file
    with open(app_py_path, 'w') as file:
        file.write(updated_content)
    
    print(f"Updated database URL in {app_py_path}")
    return True

# Run the function
if __name__ == "__main__":
    update_app_py()
