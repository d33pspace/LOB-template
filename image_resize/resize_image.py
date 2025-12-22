import os
from PIL import Image

INPUT_DIR = r"C:\Users\EDWAZHAO\OneDrive - Schenker AG\Desktop\霁觅\20251205_new_4_products\白茶"
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
    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        output_name = os.path.splitext(filename)[0] + ".jpg"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        compress_image(input_path, output_path)

if __name__ == "__main__":
    process_folder()
