# Image Optimizer

Ever had the problem that you are running out of storage because there is just no option on your phone to configure the camera settings for optimization properly? And so you move all your pictures from your phone to your PC, but now that is full instead? 
Well, this tool aims to optimize the disk size of these images!
At the moment all it does is to reduce the image (pixel) size, but other methods can be added in the future if needed.

## Requirements

- Python
- Install the required packages with pip:

```pip install -r requirements.txt```

## Backup

Since photos are our most valuable data, I strongly recommend creating a copy of your photo directory first, to test if the results are acceptable. Once you're familiar with this tool, and tested it out with all kinds of file format you may have, you can skip this step.

## Usage

Just point the script to your photos:

```python image_optimizer.py <path_to_photos>```

It will search for every image (recursively), and overwrite them.
It checks the pixel dimensions, and scales down, to have at most 1920 pixels for the longer side. (If an image is already inside this limit, it leaves it untouched.)

You can configure to have a different pixel limit, e.g. 720p:

```python image_optimizer.py <path_to_photos> --pixel 720```

You can also create new copies, with the optimized image file, if you do not wish to overwrite it:

```python image_optimizer.py <path_to_photos> --new```

Or just check what would happen with dry run:

```python image_optimizer.py <path_to_photos> --dry_run```

Check the help message for more information:

```python image_optimizer.py <path_to_photos> --help```
