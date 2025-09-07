#!/usr/bin/env python3
"""Test certificate rendering to debug signature display issues."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variable for local testing
os.environ['USE_LOCAL_DB'] = 'true'

from backend.minimal_app import app, PARTICIPATION_CERTIFICATE_TEMPLATE, PRESIDENT_SIGNATURE, CHAIRMAN_SIGNATURE, MDCAN_LOGO
from flask import render_template_string

print("Testing Participation Certificate Rendering...")
print(f"President signature available: {len(PRESIDENT_SIGNATURE) if PRESIDENT_SIGNATURE else 0} bytes")
print(f"Chairman signature available: {len(CHAIRMAN_SIGNATURE) if CHAIRMAN_SIGNATURE else 0} bytes")
print(f"Logo available: {len(MDCAN_LOGO) if MDCAN_LOGO else 0} bytes")

# Test within Flask app context
with app.app_context():
    try:
        test_html = render_template_string(
            PARTICIPATION_CERTIFICATE_TEMPLATE,
            name='John Doe',
            event_text='MDCAN BDM 14th - 2025',
            certificate_id='TEST-123',
            president_signature=PRESIDENT_SIGNATURE,
            chairman_signature=CHAIRMAN_SIGNATURE,
            logo=MDCAN_LOGO or ''
        )
        
        print(f"Rendering successful: {len(test_html)} bytes")
        
        # Check for data URLs in the rendered HTML
        president_data_url = f'data:image/png;base64,{PRESIDENT_SIGNATURE}' in test_html if PRESIDENT_SIGNATURE else False
        chairman_data_url = f'data:image/png;base64,{CHAIRMAN_SIGNATURE}' in test_html if CHAIRMAN_SIGNATURE else False
        
        print(f"President signature data URL in HTML: {'YES' if president_data_url else 'NO'}")
        print(f"Chairman signature data URL in HTML: {'YES' if chairman_data_url else 'NO'}")
        
        # Look for signature section in HTML
        sig_start = test_html.find('class="signature-section"')
        if sig_start > 0:
            print("\nSignature section preview:")
            sig_end = test_html.find('</div>', sig_start + 200)
            if sig_end > 0:
                sig_section = test_html[sig_start:sig_end + 6]
                print(sig_section[:800])  # First 800 chars
            else:
                print(test_html[sig_start:sig_start + 800])
        else:
            print("No signature section found!")
            
        # Look for any img tags
        img_count = test_html.count('<img')
        print(f"\nTotal <img> tags found: {img_count}")
        
        # Check for signature variable names (should not be present if rendered correctly)
        has_president_var = '{{ president_signature }}' in test_html
        has_chairman_var = '{{ chairman_signature }}' in test_html
        print(f"Unrendered president variable: {'YES (BAD)' if has_president_var else 'NO (GOOD)'}")
        print(f"Unrendered chairman variable: {'YES (BAD)' if has_chairman_var else 'NO (GOOD)'}")
        
    except Exception as e:
        print(f"Error rendering: {e}")
        import traceback
        traceback.print_exc()
