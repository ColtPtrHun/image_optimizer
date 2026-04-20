#!/usr/bin/env python3
"""
Image optimizer.

Reduce the size of image files.
"""

__author__ = 'Péter Kerekes'

import os
import shutil
import argparse
import warnings
from PIL import Image, ImageOps
import pillow_heif

MAX_DIMENSION       = 2160
SUFFIX              = "_optimized"
FORMAT_TARGET       = ".jpg"
FORMAT_UNDESIRABLE  = (".bmp", ".heic", ".heif", ".webp")

pillow_heif.register_heif_opener()

def main(directory,
         pixel_max=MAX_DIMENSION,
         keep_format=False,
         in_place=False):
    print(__doc__)

    # Check inputs
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        raise NotADirectoryError(f"{directory} is not a directory!")
    
    if pixel_max < 1:
        raise ValueError(f"Invalid argument: pixel_max={pixel_max}")

    print("Configuration:")
    print(f"\tInput directory: {directory}")
    print(f"\tMaximum dimension for smaller size (pixels): {pixel_max}")
    print(f"\tKeep image formats: {keep_format}")
    print(f"\tIn-Place: {in_place}")
    if not in_place:
        print(f"\t\tOutput directory: {directory + SUFFIX}")
    print()

    if not in_place:
        # Check output directory
        if os.path.exists(directory + SUFFIX):
            raise FileExistsError(f"{directory + SUFFIX} already exists. This is most likely " \
                                  "because you have already ran this script. Please remove " \
                                  "this directory first, and try again!")
        
        # Copy files recursively
        shutil.copytree(directory, directory + SUFFIX)
        directory = directory + SUFFIX # Set output directory

    files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))

    for file in files:
        try:
            print()
            img = Image.open(file)
            text_filename = str(file)

            # Apply EXIF orientation to pixels (fix rotation)
            img = ImageOps.exif_transpose(img)

            text_size = f"\tSize: ({img.size[0]}, {img.size[1]})"
            img, changed = __resize(img, pixel_max)
            if changed:
                text_size += f" -> ({img.size[0]}, {img.size[1]})"
            else:
                text_size += " -> unchanged"

            # Save file timestamps
            try:
                stat = os.stat(file)
                atime = stat.st_atime
                mtime = stat.st_mtime
            except:
                atime = mtime = None

            # Convert bitmaps and alien formats. Use compressed file format instead.
            ext = os.path.splitext(file)[1].lower()

            if not keep_format and ext in FORMAT_UNDESIRABLE:
                os.remove(file) # Remove current image file
                changed = True

                img = img.convert("RGB")
                file = os.path.splitext(file)[0] + FORMAT_TARGET
                text_filename += " -> " + str(file)
            else:
                text_filename += " -> unchanged"

            print(text_filename)
            print(text_size)

            # Export image while trying to preserve EXIF metadata.
            if changed: # Only if it was resized or converted.
                try:
                    exif = img.info.get("exif")
                    img.save(file, optimize=True, exif=exif)
                except Exception as e:
                    warnings.warn(f"\tWarning: Could not preserve EXIF metadata: {file} → {e}")
                    img.save(file, optimize=True)

                if atime is not None and mtime is not None:
                    os.utime(file, (atime, mtime))

        except Exception as e:
            print(f"Skipping: {file} → {e}")

def __resize(img, pixel_max):
    width, height = img.size
    ref_dimension = min(width, height)

    if ref_dimension <= pixel_max:
        # Within limit.
        return img, False

    # Scale down.
    scale = pixel_max / ref_dimension
    new_size = (int(width * scale), int(height * scale))
    # LANCZOS resampling produces best quality.
    return img.resize(new_size, Image.LANCZOS), True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',
                        help='Input directory that will be searched recursively for the images.')
    parser.add_argument('-p', '--pixel',
                        default=MAX_DIMENSION,
                        type=int,
                        help='Maximum dimension. Resize the image so that its smaller size (dimension) ' \
                             'will have at most this many pixels. (default: %(default)s)')
    parser.add_argument('-k', '--keep-format',
                        action='store_true',
                        help='Prevent converting image formats. Keep as-is.')
    parser.add_argument('-i', '--in-place',
                        action='store_true',
                        help='Do not create new files. Overwrite them in-place.')
    args = parser.parse_args()
    main(args.directory,
         args.pixel,
         args.keep_format,
         args.in_place)
