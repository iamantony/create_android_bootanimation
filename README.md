# create_android_bootanimation

Create Android bootanimation from .gif or .png images

## Usage

    $python3 create_bootanimation.py SOURCE_FOLDER WIDTH HEIGHT FPS SAVE_TO_FOLDER -ZIP

* PATH_TO_SOURCE_FOLDER - absolute path to the folder with .gif image or .png
images. If you specify .gif image, it will be unpacked to .png images.
* WIDTH - width of the device screen
* HEIGHT - height of the device screen
* FPS - speed at which images will be displayed
* SAVE_TO_FOLDER - folder where result files will be saved
* -ZIP - (optional) create bootanimation.zip with result files

## Examples

Create bootanimation.zip in '/path/to/result_folder' folder from images, that
was unpacked from example.gif, for device with HD screen resolution (1280x720)
and set FPS to 24:

    $ python3 create_bootanimation.py /path/to/example.gif 720 1280 24 /path/to/result_folder -zip

Create bootanimation.zip in '/path/to/result_folder' folder with images from
folder 'folder_with_images' for device with HD screen resolution (1920x1080)
and set FPS to 60:

    $ python3 create_bootanimation.py /path/to/folder_with_images 1080 1920 60 /path/to/result_folder

Show help:

    $ python create_bootanimation.py -h

## Additional Info

* https://forum.xda-developers.com/showthread.php?t=2756198
