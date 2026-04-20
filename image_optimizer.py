#!/usr/bin/env python3
"""
Image optimizer.

Reduce the size of image files by rescaling up to the given pixel limit.
"""

__author__ = 'Péter Kerekes'

import os
import shutil
import argparse
from PIL import Image, ImageOps

MAX_DIMENSION   = 2160
SUFFIX          = "_optimized"

def main(directory,
         pixel_max=MAX_DIMENSION,
         in_place=False,
         dry_run=False):
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
    print(f"\tIn-Place: {in_place}")
    if not in_place:
        print(f"\t\tOutput directory: {directory + SUFFIX}")
    print(f"\tDry run: {dry_run}")
    print()

    if not in_place:
        # Check output directory
        if os.path.exists(directory + SUFFIX):
            raise FileExistsError(f"{directory + SUFFIX} already exists. This is most likely " \
                                  "because you have already ran this script. Please remove " \
                                  "this directory first, and try again!")
        
        if not dry_run:
            shutil.copytree(directory, directory + SUFFIX) # Copy files recursively
            directory = directory + SUFFIX # Set output directory

    files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))

    for file in files:
        try:
            print()
            img = Image.open(file)
            print(f"{file}")

            # Apply EXIF orientation to pixels (fix rotation)
            img = ImageOps.exif_transpose(img)

            print(f"\tSize: ({img.size[0]}, {img.size[1]})", end='')
            img = __resize(img, pixel_max)

            if img is None:
                print(" -> Size OK.")
                continue

            print(f" -> ({img.size[0]}, {img.size[1]})")

            if not dry_run:
                # Preserve file timestamps
                try:
                    stat = os.stat(file)
                    atime = stat.st_atime
                    mtime = stat.st_mtime
                except:
                    atime = mtime = None

                # Export image while trying to preserve EXIF metadata
                try:
                    exif = img.info.get("exif")
                    img.save(file, optimize=True, exif=exif)
                except Exception as e:
                    print(f"\tWarning: Could not preserve EXIF metadata: {file} → {e}")
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
        return None

    # Scale down.
    scale = pixel_max / ref_dimension
    new_size = (int(width * scale), int(height * scale))
    # LANCZOS resampling produces best quality.
    return img.resize(new_size, Image.LANCZOS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',
                        help='Input directory that will be searched recursively for the images.')
    parser.add_argument('-p', '--pixel',
                        default=MAX_DIMENSION,
                        type=int,
                        help='Maximum dimension. Resize the image so that its smaller size (dimension) ' \
                             'will have at most this many pixels. (default: %(default)s)')
    parser.add_argument('-i', '--in-place',
                        action='store_true',
                        help='Do not create new files. Overwrite them in-place.')
    parser.add_argument('-d', '--dry-run',
                        action='store_true',
                        help='Dry run. Do not create/overwrite any files. Only display what would happen.')
    args = parser.parse_args()
    main(args.directory,
         args.pixel,
         args.in_place,
         args.dry_run)
