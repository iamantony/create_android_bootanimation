import argparse
import logging
import os
import tempfile
import time
import zipfile

from PIL import Image

import gifextract

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Create Android bootanimation.zip from .gif or bunch "
                    "of images")

    parser.add_argument("source", type=str, default="",
                        help="Absolute path to the GIF file or folder with images. "
                        "Expected image name format: xxxx-001.png "
                        "Where: "
                        "xxx - some image name; "
                        "001 - image number.")

    parser.add_argument("width", type=int, default=720,
                        help="Width of result images in pixels. "
                             "You should use width of the device screen")

    parser.add_argument("height", type=int, default=1280,
                        help="Height of result images in pixels. "
                             "You should use height of the device screen")

    parser.add_argument("fps", type=int, default=24,
                        help="FPS (Frames Per Second) for animation")

    parser.add_argument("save_to", default="",
                        help="path to the folder where result images should "
                             "be saved")

    parser.add_argument("--zip", action='store_true',
                        help="create bootanimation.zip with result images")

    parser.add_argument("--tolerance", type=int, default=10,
                        help="set tolerance for detecting background color. "
                        "For background detection (0, 0) pixel used")

    parser.add_argument("--colors", type=int, default=256,
                        help="set colors count for resulted images")

    parser.add_argument("--steps", type=int, default=100,
                        help="set steps count for scanning image")

    args = parser.parse_args()
    return args.source, args.width, args.height, args.fps, \
        args.save_to, args.zip, args.tolerance, args.colors, \
        args.steps


def check_args(t_source, t_width, t_height, t_fps, t_save_to,
               t_zip, t_tolerance, t_colors, t_steps):
    result = True
    if len(t_source) <= 0:
        _log.error("source path is empty")
        result = False

    if os.path.exists(t_source) is False:
        _log.error("path '{}' do not exist".format(t_source))
        result = False

    if t_width <= 0:
        _log.error("width is too small: " + str(t_width))
        result = False

    if t_height <= 0:
        _log.error("height is too small: " + str(t_height))
        result = False

    if t_fps <= 0:
        _log.error("fps is too small: " + str(t_fps))
        result = False

    if t_fps <= 0:
        _log.error("fps is too small: " + str(t_fps))
        result = False

    if len(t_save_to) <= 0:
        _log.error("save_to path is empty")
        result = False

    if t_tolerance <= 0:
        _log.error(f'background color tolerance is too small: {t_tolerance}')
        result = False

    if t_colors <= 0:
        _log.error(f'colors count is too small: {t_colors}')
        result = False

    if t_steps <= 0:
        _log.error(f'steps count is too small: {t_steps}')
        result = False

    return result


def main(t_source, t_width, t_height, t_fps, t_save_to, t_zip, t_tolerance, t_colors, t_steps):
    start = time.time()

    _log.info('start creating bootimage')

    source_dir = ""
    temp_dir = None
    if os.path.isdir(t_source):
        source_dir = t_source
    elif os.path.isfile(t_source) and get_extension(t_source) == "gif":
        temp_dir = tempfile.TemporaryDirectory()
        _log.info(f'extracting {t_source} to {temp_dir.name}')
        gifextract.processImage(t_source, temp_dir.name)
        source_dir = temp_dir.name
        _log.debug(f'gif extracted to {source_dir}')
    else:
        _log.error("invalid source path: " + t_source)
        return

    images = get_images_paths(source_dir)
    if len(images) <= 0:
        _log.error("no images to process")
        return

    if not os.path.exists(t_save_to):
        os.makedirs(t_save_to)

    path_to_desc_file = create_desc_file(t_save_to, t_width, t_height, t_fps)

    dir_for_images = t_save_to + "/part0"
    if not os.path.exists(dir_for_images):
        os.makedirs(dir_for_images)

    _log.info(f'{len(images)} images are ready to process')
    for idx, img in enumerate(images):
        transform_images(img, idx, t_width, t_height, dir_for_images, t_tolerance, t_colors, t_steps)

    with open(path_to_desc_file, "a") as f:
        print("p 1 0 part0", file=f)

    if t_zip is True:
        zip_file = zipfile.ZipFile(t_save_to + "/bootanimation.zip", mode="w",
                                   compression=zipfile.ZIP_STORED)

        zip_file.write(path_to_desc_file,
                       arcname=os.path.basename(path_to_desc_file))

        zip_dir(dir_for_images, zip_file)
        zip_file.close()

    end = time.time()
    _log.info(f'done in {end - start} seconds')


def get_extension(t_path):
    path_parts = str.split(t_path, '.')
    extension = path_parts[-1:][0]
    extension = extension.lower()
    return extension


def get_images_paths(t_folder):
    if not os.path.isdir(t_folder):
        return list()

    image_extensions = ("jpg", "jpeg", "bmp", "png", "tiff")
    images = list()
    entries = os.listdir(t_folder)
    for entry in entries:
        file_path = os.path.join(t_folder, entry)
        extension = get_extension(file_path)
        if os.path.isfile(file_path) and extension in image_extensions:
            images.append(file_path)

    images.sort()
    return images


def create_desc_file(t_folder, t_width, t_height, t_fps):
    file_name = t_folder + "/desc.txt"
    fd = open(file_name, mode="w+")
    print("{} {} {}".format(t_width, t_height, t_fps), file=fd)
    return file_name


def compare_colors(color_a, color_b, tolerance=10):
    return abs(color_a[0] - color_b[0]) < tolerance and \
        abs(color_a[1] - color_b[1]) < tolerance and \
        abs(color_a[2] - color_b[2]) < tolerance


def crop_image(image, tolerance, steps=100):
    """Crop image"""

    image_pixels = image.load()

    # Get background color
    background_color = image_pixels[0, 0]

    _log.debug(f'using background color {background_color}')

    # Get image crop coords
    crop_start_x = image.width
    crop_start_y = image.height
    crop_end_x = 0
    crop_end_y = 0

    for x in range(0, image.width - 1, int(image.width / steps)):
        for y in range(0, image.height - 1, int(image.height / steps)):
            if not compare_colors(image_pixels[x, y], background_color, tolerance):
                if x < crop_start_x:
                    crop_start_x = x
                if y < crop_start_y:
                    crop_start_y = y
                if x > crop_end_x:
                    crop_end_x = x
                if y > crop_end_y:
                    crop_end_y = y

    crop_start_x = max(crop_start_x - int(image.width / steps), 0)
    crop_start_y = max(crop_start_y - int(image.height / steps), 0)
    crop_end_x = min(crop_end_x + int(image.width / steps), image.width - 1)
    crop_end_y = min(crop_end_y + int(image.height / steps), image.height - 1)

    # Get only 1 pixel if start > end
    if crop_start_x > crop_end_x:
        crop_start_x = 0
        crop_end_x = 1
    if crop_start_y > crop_end_y:
        crop_start_y = 0
        crop_end_y = 1

    _log.debug(f'crop coords: ({crop_start_x},{crop_start_y}) - '
               f'({crop_end_x}, {crop_end_y})')

    # Crop image
    cropped_image = image.crop((crop_start_x, crop_start_y,
                                crop_end_x, crop_end_y))

    _log.debug(f'trim: {cropped_image.width}x{cropped_image.height}+{crop_start_x}+{crop_start_y}')

    return {
        'image': cropped_image,
        'pos_x': crop_start_x,
        'pos_y': crop_start_y
    }


def transform_images(t_img_path, t_count, t_width, t_height, t_save_to_path,
                     t_tolerance, t_colors, t_steps):
    _log.info(f'processing image {t_count}: {t_img_path}')

    original_img = Image.open(t_img_path)

    # Scale image
    width_percent = (t_width / float(original_img.width))
    height_size = int((float(original_img.height) * float(width_percent)))
    original_img = original_img.resize((t_width, height_size), Image.LANCZOS)

    result_image = Image.new("RGB", (t_width, t_height), original_img.getpixel((0, 0)))

    width_pos = 0
    height_pos = int(t_height / 2 - original_img.height / 2)
    result_image.paste(original_img, (width_pos, height_pos))

    # Crop image
    _log.debug(f'size before crop: {result_image.width}x{result_image.height}')
    crop_result = crop_image(result_image, tolerance=t_tolerance, steps=t_steps)
    result_image = crop_result['image']
    _log.debug(f'size after crop: {result_image.width}x{result_image.height}')

    fd = open(t_save_to_path + '/' + 'trim.txt', mode="a+")
    print(f'{result_image.width}x{result_image.height}'
          f'+{crop_result["pos_x"]}+{crop_result["pos_y"]}', file=fd)

    # Convert image to adaptive palette colors
    result_image = result_image.convert('P', palette=Image.ADAPTIVE, colors=t_colors)

    result_img_name = "{0:0{width}}.png".format(t_count, width=5)
    result_img_path = t_save_to_path + "/" + result_img_name
    result_image.save(result_img_path)


def zip_dir(t_path, t_zip_file):
    path_head, last_dir = os.path.split(t_path)
    images = get_images_paths(t_path)
    for img in images:
        img_path_in_zip = last_dir + "/" + os.path.basename(img)
        t_zip_file.write(img, arcname=img_path_in_zip,
                         compress_type=zipfile.ZIP_STORED)


if __name__ == '__main__':
    arguments = parse_arguments()
    if check_args(*arguments) is True:
        main(*arguments)
