#!/usr/bin/env python3
"""
Test script to verify app routes and functionality
"""
import sys
import os

# Add the backend directory to path
sys.path.insert(0, '.')

try:
    from minimal_app import app
    print("✓ App import successful")
    
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {rule.rule} [{methods}]")
    
    print(f"\nStatic folder: {getattr(app, 'static_folder', 'Not set')}")
    
    # Test if frontend files exist
    frontend_paths = [
        'frontend/build',
        '../frontend/build',
        './frontend/build',
        '/app/frontend/build',
        'build',
    ]
    
    print("\nFrontend build status:")
    for path in frontend_paths:
        index_path = os.path.join(path, 'index.html')
        exists = os.path.exists(index_path)
        print(f"  {path}/index.html: {'✓ EXISTS' if exists else '✗ NOT FOUND'}")
    
    print("\n✓ All checks completed successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
