# create_android_bootanimation

[![Build Status](https://travis-ci.org/iamantony/create_android_bootanimation.svg?branch=master)](https://travis-ci.org/iamantony/create_android_bootanimation)

Create Android bootanimation from .gif or .png images

## Fast bash commands

```bash
python create_bootanimation.py ../input/1 1440 3120 50 ../input/output/1 --steps 200 --colors 16 --tolerance 1
python create_bootanimation.py ../input/2 1440 3120 50 ../input/output/2 --steps 200 --colors 16 --tolerance 1

zip -0qry -i \*.txt \*.png \*.wav @ ../bootanimation.zip *.txt part*
```

## Usage

usage: `create_bootanimation.py [-h] [--zip] [--tolerance TOLERANCE] [--colors COLORS] source width height fps save_to`

Create Android bootanimation.zip from .gif or bunch of images

positional arguments:

- `source` - Absolute path to the GIF file or folder with images. Expected image name format: xxxx-001.png Where: xxx -
  some image name; 001 - image number.
- `width` - Width of result images in pixels. You should use width of the device screen
- `height` - Height of result images in pixels. You should use height of the device screen
- `fps` - FPS (Frames Per Second) for animation
- `save_to` - path to the folder where result images should be saved

optional arguments:

- `-h, --help` - show this help message and exit
- `--zip` - create bootanimation.zip with result images
- `--tolerance TOLERANCE` - set tolerance for detecting background color. For background detection (0, 0) pixel used
- `--colors COLORS` - set colors count for resulted images

## Examples

Create bootanimation.zip in '/path/to/result_folder' folder from images, that was unpacked from example.gif, for device
with HD screen resolution (1280x720) and set FPS to 24:

    $ python3 create_bootanimation.py /path/to/example.gif 720 1280 24 /path/to/result_folder -zip

Create bootanimation.zip in '/path/to/result_folder' folder with images from folder 'folder_with_images' for device with
HD screen resolution (1920x1080) and set FPS to 60:

    $ python3 create_bootanimation.py /path/to/folder_with_images 1080 1920 60 /path/to/result_folder

Show help:

    $ python3 create_bootanimation.py -h

## Additional Info

- https://forum.xda-developers.com/showthread.php?t=2756198
