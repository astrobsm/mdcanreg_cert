from PIL import Image
import numpy as np

def analyze_signature_deeply(filename):
    print(f'\n=== DEEP ANALYSIS: {filename} ===')
    try:
        with Image.open(filename) as img:
            print(f'Mode: {img.mode}')
            print(f'Size: {img.size}')
            print(f'Has transparency info: {"transparency" in img.info}')
            
            # Convert to numpy for detailed analysis
            data = np.array(img)
            
            if img.mode == 'RGBA':
                r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
                
                # Check for white/near-white pixels
                white_pixels = (r > 240) & (g > 240) & (b > 240)
                white_count = np.sum(white_pixels)
                total_pixels = r.size
                white_percentage = (white_count / total_pixels) * 100
                
                print(f'Total pixels: {total_pixels:,}')
                print(f'White/near-white pixels: {white_count:,} ({white_percentage:.1f}%)')
                
                # Check alpha values for white pixels
                white_alpha_values = a[white_pixels]
                if len(white_alpha_values) > 0:
                    unique_white_alphas = np.unique(white_alpha_values)
                    print(f'Alpha values for white pixels: {unique_white_alphas}')
                    
                    if 255 in unique_white_alphas:
                        opaque_white_count = np.sum(white_alpha_values == 255)
                        print(f'❌ PROBLEM: {opaque_white_count:,} white pixels are OPAQUE (alpha=255)')
                        print(f'❌ This creates visible white background!')
                    else:
                        print(f'✅ All white pixels are transparent')
                
                # Overall alpha analysis
                unique_alphas = np.unique(a)
                print(f'Alpha range: {np.min(a)} to {np.max(a)}')
                print(f'Number of different alpha values: {len(unique_alphas)}')
                
                # Check corners for background detection
                corner_size = 50
                corners = [
                    data[:corner_size, :corner_size],  # top-left
                    data[:corner_size, -corner_size:], # top-right
                    data[-corner_size:, :corner_size], # bottom-left
                    data[-corner_size:, -corner_size:] # bottom-right
                ]
                
                print('Corner analysis:')
                for i, corner_name in enumerate(['top-left', 'top-right', 'bottom-left', 'bottom-right']):
                    corner_data = corners[i]
                    avg_alpha = np.mean(corner_data[:,:,3])
                    avg_rgb = np.mean(corner_data[:,:,:3], axis=(0,1))
                    print(f'  {corner_name}: avg_alpha={avg_alpha:.1f}, avg_RGB=({avg_rgb[0]:.1f},{avg_rgb[1]:.1f},{avg_rgb[2]:.1f})')
                    if avg_alpha > 200 and np.all(avg_rgb > 240):
                        print(f'    ❌ {corner_name} has opaque white background')
                    elif avg_alpha < 50:
                        print(f'    ✅ {corner_name} is transparent')
            
            else:
                print(f'❌ Image is not in RGBA mode, cannot have transparency')
                
    except Exception as e:
        print(f'Error analyzing {filename}: {e}')

# Analyze all signatures
for sig in ['president-signature.png', 'chairman-signature.png', 'Dr_Augustine_Duru_signature.png']:
    try:
        analyze_signature_deeply(sig)
    except FileNotFoundError:
        print(f'File not found: {sig}')
