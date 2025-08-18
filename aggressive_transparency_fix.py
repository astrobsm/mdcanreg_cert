from PIL import Image
import numpy as np
import os

def aggressive_transparency_fix(image_path, output_path=None):
    """Aggressive white background removal for signatures"""
    if output_path is None:
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_aggressive_transparent{ext}"
    
    try:
        with Image.open(image_path) as img:
            print(f"\n🔧 AGGRESSIVE TRANSPARENCY FIX: {os.path.basename(image_path)}")
            print(f"Original mode: {img.mode}, Size: {img.size}")
            
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Convert to numpy array
            data = np.array(img)
            red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
            
            # Strategy 1: Remove ALL light pixels (very aggressive)
            threshold_aggressive = 230  # Much lower threshold
            light_pixels_aggressive = (red > threshold_aggressive) & (green > threshold_aggressive) & (blue > threshold_aggressive)
            
            # Strategy 2: Edge detection - preserve edges, remove uniform areas
            from scipy import ndimage
            
            # Calculate gradients to find edges
            grad_r = np.abs(ndimage.sobel(red.astype(float)))
            grad_g = np.abs(ndimage.sobel(green.astype(float)))
            grad_b = np.abs(ndimage.sobel(blue.astype(float)))
            
            # Combine gradients
            total_gradient = grad_r + grad_g + grad_b
            
            # Pixels with low gradient are likely background
            low_gradient = total_gradient < 10  # Adjust as needed
            
            # Strategy 3: Color similarity clustering
            # Group similar colors and remove the most common light color
            
            # Combine strategies
            # Remove light pixels that are NOT on edges
            background_pixels = light_pixels_aggressive & low_gradient
            
            print(f"Pixels to make transparent: {np.sum(background_pixels):,}")
            
            # Make background transparent
            data[background_pixels] = [255, 255, 255, 0]
            
            # Additional cleanup: remove pixels that are very similar to white
            for threshold in [250, 245, 240, 235]:
                similar_to_white = (
                    (red > threshold) & (green > threshold) & (blue > threshold) &
                    (alpha > 200)  # Only if currently opaque
                )
                count = np.sum(similar_to_white)
                if count > 0:
                    data[similar_to_white] = [255, 255, 255, 0]
                    print(f"Removed {count:,} pixels at threshold {threshold}")
            
            # Create new image
            new_img = Image.fromarray(data, 'RGBA')
            
            # Save result
            new_img.save(output_path, 'PNG')
            print(f"✅ Saved aggressively cleaned version: {output_path}")
            
            # Verify result
            alpha_values = set()
            for pixel in new_img.getdata():
                alpha_values.add(pixel[3])
            print(f"Final alpha values: {sorted(alpha_values)}")
            
            return output_path
            
    except ImportError:
        print("⚠️ scipy not available, using basic method")
        return basic_transparency_fix(image_path, output_path)
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def basic_transparency_fix(image_path, output_path):
    """Basic transparency fix without scipy"""
    with Image.open(image_path) as img:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        data = np.array(img)
        red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        
        # Very aggressive threshold
        for threshold in [250, 245, 240, 235, 230, 225]:
            light_pixels = (red > threshold) & (green > threshold) & (blue > threshold) & (alpha > 100)
            data[light_pixels] = [255, 255, 255, 0]
        
        new_img = Image.fromarray(data, 'RGBA')
        new_img.save(output_path, 'PNG')
        return output_path

if __name__ == "__main__":
    # Fix all signatures with aggressive method
    signatures = ['president-signature.png', 'chairman-signature.png', 'Dr_Augustine_Duru_signature.png']
    
    for sig in signatures:
        if os.path.exists(sig):
            print(f"\n{'='*60}")
            result = aggressive_transparency_fix(sig)
            if result:
                print(f"✅ Created: {result}")
                
                # Option to replace original
                replace = input(f"Replace original {sig} with cleaned version? (y/N): ").strip().lower()
                if replace in ['y', 'yes']:
                    os.replace(result, sig)
                    print(f"✅ Replaced {sig}")
        else:
            print(f"❌ {sig} not found")
