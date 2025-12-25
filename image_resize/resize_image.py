import os
from PIL import Image

INPUT_DIR = r"C:\Users\EDWAZHAO\OneDrive - Schenker AG\Desktop\霁觅\20251205_new_4_products\古树生普"
OUTPUT_DIR = os.path.join(INPUT_DIR, "update")
MAX_SIZE_KB = 500
MAX_SIZE_BYTES = MAX_SIZE_KB * 1024

os.makedirs(OUTPUT_DIR, exist_ok=True)

def compress_image(input_path, output_path):
    img = Image.open(input_path)
    img = img.convert("RGB")  # ensure compatibility (especially for PNG)

    # Initial resize if image is very large
    max_width = 3000
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    quality = 95
    min_quality = 25
    while quality >= min_quality:
        img.save(
            output_path,
            format="JPEG",
            quality=quality,
            optimize=True
        )

        if os.path.getsize(output_path) <= MAX_SIZE_BYTES:
            print(f"✅ {os.path.basename(output_path)} saved at quality={quality}")
            return

        quality -= 5

    print(f"⚠️ {os.path.basename(output_path)} reached minimum quality {min_quality}")

def process_folder():
    # Counters for each type
    counters = {"m": 0, "x": 0, "d": 0, "other": 0}
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(INPUT_DIR):
        # Skip the OUTPUT_DIR itself
        if root == OUTPUT_DIR or OUTPUT_DIR in root:
            continue
            
        # Get the folder name to determine prefix
        folder_name = os.path.basename(root)
        
        # Determine prefix based on folder name
        if "主图" in folder_name:
            prefix = "m"
        elif "规格" in folder_name:
            prefix = "x"
        elif "详情" in folder_name:
            prefix = "d"
        else:
            prefix = None
        
        # Process each image in this directory
        for filename in sorted(files):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            
            input_path = os.path.join(root, filename)
            
            # Generate output filename with prefix
            if prefix:
                counters[prefix] += 1
                output_name = f"{prefix}{counters[prefix]:02d}.jpg"
            else:
                counters["other"] += 1
                output_name = f"other_{counters['other']:02d}.jpg"
            
            output_path = os.path.join(OUTPUT_DIR, output_name)
            
            print(f"Processing: {os.path.relpath(input_path, INPUT_DIR)} → {output_name}")
            compress_image(input_path, output_path)

if __name__ == "__main__":
    process_folder()
