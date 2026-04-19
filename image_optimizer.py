#!/usr/bin/env python3
"""
Image optimizer.

Reduce the size of image files by rescaling up to the given pixel limit.
"""

__author__ = 'Péter Kerekes'

import argparse
import os
from PIL import Image

MAX_DIMENSION   = 1920
PREFIX          = "_optimized_"

def main(directory,
         overwrite=True,
         pixel_max=MAX_DIMENSION,
         dry_run=False):
    print(__doc__)

    # Check inputs
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        raise NotADirectoryError(f"{directory} is not a directory!")
    
    if pixel_max < 1:
        raise ValueError(f"Invalid argument: pixel_max={pixel_max}")

    print("Configuration:")
    print(f"\tDirectory: {directory}")
    print(f"\tOverwrite: {overwrite}")
    print(f"\tMaximum dimension (pixels): {pixel_max}")
    print(f"\tDry run: {dry_run}")
    print()

    files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))

    for file in files:
        try:
            print()
            img = Image.open(file)
            print(f"{file}", end='')

            if overwrite:
                path = file
                print()
            else:
                path = os.path.join(os.path.dirname(file), PREFIX + os.path.basename(file))
                if os.path.exists(path): # With copy option let's not delete/overwrite any files.
                    print(f"Error: {path} already exists!")
                    return # Do not continue with the next file. Investigate.
                print(f" -> {path}")

            print(f"\tSize: ({img.size[0]}, {img.size[1]})", end='')
            img, resized = __resize(img, pixel_max)

            if not resized:
                print(" -> Size OK.")
                continue

            print(f" -> ({img.size[0]}, {img.size[1]})")

            if not dry_run:
                if os.path.exists(path):
                    os.remove(path)
                img.save(path, optimize=True)

        except Exception as e:
            print(f"Skipping: {file} → {e}")

def __resize(img, pixel_max):
    width, height = img.size
    max_dim = max(width, height)

    if max_dim <= pixel_max:
        # Within limit. Return untouched.
        return img, False

    # Scale down.
    scale = pixel_max / max_dim
    new_size = (int(width * scale), int(height * scale))
    # LANCZOS resampling produces best quality.
    return img.resize(new_size, Image.LANCZOS), True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',
                        help='Input directory that will be searched recursively for the images.')
    parser.add_argument('-n', '--new',
                        action='store_true',
                        help='Create new image files instead of overwriting.')
    parser.add_argument('-p', '--pixel',
                        default=MAX_DIMENSION,
                        type=int,
                        help='Maximum dimension. Resize the image so that its larger dimension ' \
                             'will have at most this many pixels. (default: %(default)s)')
    parser.add_argument('-d', '--dry_run',
                        action='store_true',
                        help='Dry run.')
    args = parser.parse_args()
    main(args.directory,
         not args.new,
         args.pixel,
         args.dry_run)
