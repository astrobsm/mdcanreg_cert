import sys
import os
from PIL import Image

def check_transparency(image_path):
    """Check if a PNG image has transparency"""
    try:
        with Image.open(image_path) as img:
            print(f"\n=== {os.path.basename(image_path)} ===")
            print(f"Mode: {img.mode}")
            print(f"Size: {img.size}")
            print(f"Has transparency: {img.mode in ('RGBA', 'LA') or 'transparency' in img.info}")
            
            if img.mode == 'RGBA':
                print("✅ Image has alpha channel (RGBA)")
                # Check if alpha channel is actually used
                alpha_values = set()
                for pixel in img.getdata():
                    alpha_values.add(pixel[3])  # Alpha is the 4th component
                print(f"Alpha values found: {sorted(alpha_values)}")
                if len(alpha_values) > 1:
                    print("✅ Image uses transparency (multiple alpha values)")
                else:
                    if 255 in alpha_values:
                        print("⚠️ Image has alpha channel but appears fully opaque")
                    else:
                        print("⚠️ Image appears fully transparent")
            elif img.mode == 'P' and 'transparency' in img.info:
                print("✅ Image has palette transparency")
            elif img.mode == 'RGB':
                print("❌ Image is RGB only (no transparency)")
            else:
                print(f"ℹ️ Image mode: {img.mode}")
                
            return img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            
    except Exception as e:
        print(f"❌ Error checking {image_path}: {e}")
        return False

if __name__ == "__main__":
    signatures = [
        "president-signature.png",
        "chairman-signature.png", 
        "Dr_Augustine_Duru_signature.png"
    ]
    
    print("MDCAN Certificate Signature Transparency Check")
    print("=" * 50)
    
    for sig in signatures:
        if os.path.exists(sig):
            check_transparency(sig)
        else:
            print(f"\n❌ {sig} not found")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("• RGBA mode = Has alpha channel for transparency")
    print("• RGB mode = No transparency (solid background)")
    print("• Multiple alpha values = Transparency is actually used")
