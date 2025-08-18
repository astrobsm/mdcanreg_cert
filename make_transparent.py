import sys
import os
from PIL import Image
import numpy as np

def make_transparent(image_path, output_path=None):
    """Make white/light backgrounds transparent"""
    if output_path is None:
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_transparent{ext}"
    
    try:
        with Image.open(image_path) as img:
            print(f"Processing: {os.path.basename(image_path)}")
            print(f"Original mode: {img.mode}, Size: {img.size}")
            
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Convert to numpy array for easier processing
            data = np.array(img)
            
            # Define white/light color threshold
            # Pixels with RGB values above this threshold will be made transparent
            threshold = 240  # Adjust this value as needed (0-255)
            
            # Create transparency mask
            # Make pixels transparent if they are close to white
            red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
            
            # Identify pixels that are close to white/light gray
            light_pixels = (red > threshold) & (green > threshold) & (blue > threshold)
            
            # Make light pixels transparent
            data[light_pixels] = [255, 255, 255, 0]  # White but fully transparent
            
            # Create new image from modified data
            new_img = Image.fromarray(data, 'RGBA')
            
            # Save the result
            new_img.save(output_path, 'PNG')
            print(f"✅ Saved transparent version: {output_path}")
            
            # Check the result
            print("Checking transparency...")
            alpha_values = set()
            for pixel in new_img.getdata():
                alpha_values.add(pixel[3])
            print(f"Alpha values in result: {sorted(alpha_values)}")
            
            if len(alpha_values) > 1:
                print("✅ Transparency successfully added!")
            else:
                print("⚠️ No transparency change detected - may need manual editing")
                
            return output_path
            
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return None

if __name__ == "__main__":
    input_file = "president-signature.png"
    output_file = "president-signature-transparent.png"
    
    if os.path.exists(input_file):
        result = make_transparent(input_file, output_file)
        if result:
            print(f"\n🎯 Use this command to replace the signature:")
            print(f"Copy-Item '{result}' 'president-signature.png' -Force")
    else:
        print(f"❌ {input_file} not found")
        print("Available files:")
        for f in os.listdir('.'):
            if 'signature' in f.lower():
                print(f"  {f}")
