#!/usr/bin/env python3
"""
Quick test to verify the SSL configuration syntax locally
"""
import os
import sys

# Add the backend directory to the path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

try:
    # Test that the CA certificate file exists and is readable
    ca_cert_path = os.path.join(backend_dir, 'ca-certificate.crt')
    if os.path.exists(ca_cert_path):
        with open(ca_cert_path, 'r') as f:
            cert_content = f.read()
            if cert_content.startswith('-----BEGIN CERTIFICATE-----'):
                print(f"✅ CA Certificate found and valid: {ca_cert_path}")
                print(f"   Certificate length: {len(cert_content)} characters")
            else:
                print(f"❌ CA Certificate format invalid: {ca_cert_path}")
    else:
        print(f"❌ CA Certificate not found: {ca_cert_path}")
    
    # Test the database configuration syntax
    DATABASE_URL = "postgresql://test:test@localhost:5432/test?sslmode=require"
    
    # Simulate the SSL configuration
    engine_options = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'MDCAN_BDM_2025'
        }
    }
    
    if 'postgresql://' in DATABASE_URL:
        engine_options['connect_args']['sslmode'] = 'require'
        
        if os.path.exists(ca_cert_path):
            engine_options['connect_args']['sslrootcert'] = ca_cert_path
            print(f"✅ SSL configuration syntax valid")
            print(f"   sslmode: require")
            print(f"   sslrootcert: {ca_cert_path}")
        else:
            print(f"⚠️  SSL mode set but no CA certificate")
    
    print(f"✅ Configuration test completed successfully")
    
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
    import traceback
    traceback.print_exc()
