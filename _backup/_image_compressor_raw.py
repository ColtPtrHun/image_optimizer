import os
from PIL import Image, ExifTags
import pillow_heif

pillow_heif.register_heif_opener()

TARGET_MIN_DIM = 2160

SUPPORTED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".heif"
)

def fix_rotation(img):
    try:
        exif = img._getexif()
        if exif is None:
            return img

        orientation_key = next(
            key for key, value in ExifTags.TAGS.items()
            if value == "Orientation"
        )

        orientation = exif.get(orientation_key)

        if orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 6:
            img = img.rotate(270, expand=True)
        elif orientation == 8:
            img = img.rotate(90, expand=True)

    except Exception:
        pass

    return img


def resize(img):
    width, height = img.size
    min_dim = min(width, height)

    if min_dim <= TARGET_MIN_DIM:
        return img, False

    scale = TARGET_MIN_DIM / min_dim
    new_size = (int(width * scale), int(height * scale))

    return img.resize(new_size, Image.LANCZOS), True


def has_transparency(img):
    if img.mode in ("RGBA", "LA"):
        return True
    if img.mode == "P":
        return "transparency" in img.info
    return False


def process_image(path):
    try:
        ext = os.path.splitext(path)[1].lower()

        img = Image.open(path)
        img = fix_rotation(img)

        img, resized = resize(img)

        base = os.path.splitext(path)[0]

        # ---- FORMAT LOGIC ----

        if ext in (".jpg", ".jpeg"):
            img = img.convert("RGB")
            img.save(path, "JPEG", quality=90, optimize=True)

        elif ext == ".png":
            if has_transparency(img):
                img.save(path, "PNG", optimize=True)
            else:
                new_path = base + ".jpg"
                img = img.convert("RGB")
                img.save(new_path, "JPEG", quality=90, optimize=True)
                os.remove(path)
                path = new_path

        elif ext == ".webp":
            img.save(path, "WEBP", quality=90, method=6)

        elif ext in (".heic", ".heif"):
            new_path = base + ".jpg"
            img = img.convert("RGB")
            img.save(new_path, "JPEG", quality=90, optimize=True)
            os.remove(path)
            path = new_path

        elif ext == ".bmp":
            new_path = base + ".jpg"
            img = img.convert("RGB")
            img.save(new_path, "JPEG", quality=90, optimize=True)
            os.remove(path)
            path = new_path

        print(f"Processed: {path} ({'resized' if resized else 'kept size'})")

    except Exception as e:
        print(f"Error: {path} → {e}")


def process_folder(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                process_image(os.path.join(root, file))
            else:
                print(f"{file} has unsupported file format. Skipping.")


if __name__ == "__main__":
    folder = input("Enter folder path: ").strip()
    process_folder(folder)
