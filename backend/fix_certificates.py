"""
Fix certificate image paths by updating the HTML template to use the new serve_asset endpoint
"""

import os

def main():
    # Read app.py
    app_path = 'app.py'
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the template section that contains the image tags with file:// prefix
    template_start = content.find('CERTIFICATE_HTML = """')
    if template_start == -1:
        print("Could not find CERTIFICATE_HTML template!")
        return
    
    # Replace the image tags with our new endpoint
    updated_content = content.replace('src="file://{{ mdcan_logo }}"', 
                                    'src="/serve_asset/{{ mdcan_logo.split(\'/\')[-1] if mdcan_logo and \'/\' in mdcan_logo else \'mdcan-logo.png\' }}"')
    updated_content = updated_content.replace('src="file://{{ coalcity_logo }}"', 
                                            'src="/serve_asset/{{ coalcity_logo.split(\'/\')[-1] if coalcity_logo and \'/\' in coalcity_logo else \'coalcity-logo.png\' }}"')
    updated_content = updated_content.replace('src="file://{{ president_signature }}"', 
                                            'src="/serve_asset/{{ president_signature.split(\'/\')[-1] if president_signature and \'/\' in president_signature else \'president-signature.png\' }}"')
    updated_content = updated_content.replace('src="file://{{ chairman_signature }}"', 
                                            'src="/serve_asset/{{ chairman_signature.split(\'/\')[-1] if chairman_signature and \'/\' in chairman_signature else \'chairman-signature.png\' }}"')
    
    if content == updated_content:
        print("No changes were made. The file:// prefixes might not be in the expected format.")
        return
    
    # Write back the updated content
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Certificate template updated successfully!")

if __name__ == "__main__":
    main()
