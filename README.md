# Image Optimizer

Ever had the problem that you are running out of storage because there is just no option on your phone to configure the camera settings for optimization properly? And so you move all your pictures from your phone to your PC, but now that is full instead? 
Well, this tool aims to optimize the disk size of these images!
Currently this tool:
- reduces the image (pixel) size,
- convert unefficent/unknown formats to jpg,
- and export the image with optimization.

> Note: Often video files can occupy a lot of storage as well, but that is out of the scope of this tool. Keep in mind, that you may want to reduce their size as well with a different tool.

## Requirements

- Python
- Install the required packages with pip:

```pip install -r requirements.txt```

## Usage

Just point the script to your photos:

```python image_optimizer.py <path_to_photos>```

First, the directory is copied (recursively) with suffix: *_optimized* (e.g: */c/pictures/* -> */c/pictures_optimized/*).
In the new directory, every image is checked: the smaller side (dimension) shall have at most 2160 pixels.
The image is then scaled down if outside this limit while keeping its aspect ratio. Unefficent or unpopular formats are converted to *jpg*. The file/image metadata is kept.

If you wish to keep the original format:

```python image_optimizer.py <path_to_photos> --keep-format```

You can configure to have a different pixel limit, e.g. 1080p:

```python image_optimizer.py <path_to_photos> --pixel 1080```

You can also overwrite the files in-place (without copying the directory).

> Note: Only use this option if you know what you're doing. Since photos are our most valuable data, I only recommend this option when you are already familiar with this tool, tested with all kinds of file format you may have, and you are satisfied with the results.

```python image_optimizer.py <path_to_photos> --in-place```

Or just check what would happen with dry run:

```python image_optimizer.py <path_to_photos> --dry-run```

Check the help message for more information:

```python image_optimizer.py <path_to_photos> --help```
