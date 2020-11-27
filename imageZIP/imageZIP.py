from PIL import Image
import io
import os
import math
from sys import platform

Image.MAX_IMAGE_PIXELS = None
ON_WINDOWS = platform == 'win32'


def _calculate_color(num, color_mode: str):
    """
    Calculate color for input byte, represented as 0<=int<=255 (or special float code)
    """

    color_max = 255

    if type(num) == float:
        if num == 0.:
            return 255, 250, 255
        elif num == 1.:
            return 5, 0, 5

    if color_mode in ['heat_toxic', 'heat_map_toxic']:
        # original num is always be 0 <= num <= 255 (it's actually 256 different bytes)
        # by multiplying num, we are getting wider range of colors
        num *= 4
        # all pallets multiplied and divided by num should be equal 256 to store right amount of data
        # palettes is a ranges of colors to store data in
        palette1 = 256
        # color_min and color_max is a color range of palette1
        # Don't forget that 0 counts, so full range from color_min to color_max is 256, not 255
        color_min = 0

    elif color_mode in ['heat', 'heat_map']:
        num *= 3
        palette1 = 192
        color_min = 20
    elif color_mode == 'bw':
        return num, num, num
    elif color_mode == 'rainbow':
        num *= 5
        palette1 = 183  # imperfect, actually 182.85
        color_min = 20
    elif color_mode == 'red':
        return color_max, color_max-num, color_max-num
    elif color_mode == 'blue':
        return color_max-num, color_max-num, color_max
    else:
        raise AttributeError(f'"{color_mode}" color_mode does not exist.')

    color_max = color_min + palette1 - 1
    palette2 = palette1 * 2
    palette3 = palette2 + palette1

    if color_mode == 'rainbow':
        palette4 = palette3 + palette1
        palette5 = palette4 + palette1
        palette6 = palette5 + palette1
        if num < palette1:
            return color_max, color_max-num, color_max-num
        if num < palette2:
            num -= palette1
            return color_max, color_min+num, color_min
        elif num < palette3:
            num -= palette2
            return color_max-num, color_max, color_min
        elif num < palette4:
            num -= palette3
            return color_min, color_max, color_min+num
        elif num < palette5:
            num -= palette4
            return color_min, color_max-num, color_max
        elif num < palette6:
            num -= palette5
            return color_min + num, color_min, color_max
        else:
            num -= palette6
            return color_max-num, color_min, color_max-num
    else:
        if num < palette1:
            return color_min, color_min + num, color_max
        elif num < palette2:
            num -= palette1
            return color_min, color_max, color_max - num
        elif num < palette3:
            num -= palette2
            return color_min + num, color_max, color_min
        else:
            num -= palette3
            return color_max, color_max - num, color_min


def _calculate_sizes(multiplier, perimeter):
    """
    Calculate sizes of final zip image
    """

    mult_orig = multiplier
    mult_stop = mult_orig / 2.5
    while multiplier > mult_stop:
        a = perimeter / multiplier
        if a % 1 == 0:
            b = perimeter / a
            return int(min([a, b])), int(max([a, b]))
        multiplier -= 1
    return mult_orig, mult_orig


def decrypt_image(path, color_mode, scale, file_chosen):
    """
    Unzips files and directories from an image file (path)
    """

    path_to_save = '/'.join(os.path.split(path)[:-1])

    if not ON_WINDOWS:
        path = path.replace(os.sep, '/').replace('\\', '/')

    with open(path, 'rb') as file:
        img = file.read()
    img = Image.open(io.BytesIO(img))

    bytesDict = {}
    for i in range(256):
        bytesDict[str(_calculate_color(i, color_mode=color_mode))] = bytes([i])
    bytesDict[str(_calculate_color(0., color_mode))] = 0  # Folder delimiter
    bytesDict[str(_calculate_color(1., color_mode))] = 1  # File delimiter
    bytesDict[str((230, 235, 230))] = 2  # End of file delimiter

    end_pixel = False
    interval = []
    decrypted_file_path = False

    # Not-so-good pile of code, redesign is needed
    for row in range(int(img.height / scale)):
        for col in range(int(img.width / scale)):
            try:
                bt = bytesDict[str(img.getpixel((col * scale, row * scale)))]
            except KeyError:
                raise RuntimeError("Can't unzip from an image, settings can be incorrect or image is distorted.")
            if type(bt) == int:
                if bt == 1:
                    if not decrypted_file_path:
                        decrypted_file_path = b''.join(interval).decode('utf-8')
                        interval = []
                        continue
                    else:
                        new_path = os.path.join(path_to_save, decrypted_file_path)

                        if not ON_WINDOWS:
                            new_path = new_path.replace(os.sep, '/').replace('\\', '/')

                        with open(new_path, 'wb') as file:
                            file.writelines(interval)

                        interval = []
                        decrypted_file_path = None
                elif bt == 0:
                    decrypted_folder_path = b''.join(interval).decode('utf-8')

                    path_joined = os.path.join(path_to_save, decrypted_folder_path)

                    if not ON_WINDOWS:
                        path_joined = path_joined.replace(os.sep, '/').replace('\\', '/')

                    if not os.path.exists(path_joined):
                        os.mkdir(path_joined)
                    interval = []
                elif bt == 2:
                    end_pixel = True
                    break
            else:
                interval.append(bt)
        if end_pixel:
            break


def draw_bytes_as_image(bts, color_mode, scale, **kwargs):
    """
    Build final zip image file from bytes
    """

    bts_len = len(bts)
    bt_index = 0

    size_original = math.ceil(math.sqrt(bts_len))
    size_x, size_y = _calculate_sizes(size_original, bts_len)
    color_PIL = 'RGB'
    img = Image.new(color_PIL, (size_x * scale, size_y * scale), color='#e6ebe6')

    for row in range(size_y):
        for col in range(size_x):
            try:
                color = _calculate_color(num=bts[bt_index], color_mode=color_mode)
            except IndexError:
                break
            x, y = col * scale, row * scale
            img_block = Image.new(color_PIL, (scale, scale), color=color)
            img.paste(img_block, (x, y))
            bt_index += 1
    return img


def img_save(img, path, **kwargs):
    """
    Save final image
    """

    path = os.path.normpath(path)

    if not ON_WINDOWS:
        path = path.replace(os.sep, '/').replace('\\', '/')

    img.save(path + '_zip.png')


def encrypt_obj(path_base, path_relative, **kwargs):
    """
    Encrypt file or directory
    """

    path = os.path.join(path_base, path_relative)

    bts = [b for b in bytes(''.join([char for char in path_relative]), encoding='UTF-8')]

    if os.path.isdir(path):
        bts.append(0.)

        return bts
    else:
        bts.append(1.)

        if not ON_WINDOWS:
            path = path.replace(os.sep, '/').replace('\\', '/')

        with open(path, 'rb') as file:
            file_bytes = file.read()
        [bts.append(b) for b in file_bytes]
        bts.append(1.)
        return bts


def encrypt(path_base, path_relative, bts_zip, **kwargs):
    """
    Recursive function, which is encrypting all the inner files and directories
    """
    path = os.path.join(path_base, path_relative)
    if os.path.isdir(path):
        bts_zip += encrypt_obj(path_base=path_base, path_relative=path_relative, **kwargs)
        for name in os.listdir(path):
            path_to_name = os.path.join(path_relative, name)
            encrypt(path_base=path_base, path_relative=path_to_name, bts_zip=bts_zip, **kwargs)  # Recursion
    else:
        bts_zip += encrypt_obj(path_base=path_base, path_relative=path_relative, **kwargs)


def encrypt_hub(path, **kwargs):
    """
    Whole encryption process for file or directory
    """
    bts_zip = []
    split = os.path.split(os.path.normpath(path))
    path_base = '/'.join(split[:-1])
    path_relative = split[-1]
    encrypt(path_base=path_base, path_relative=path_relative, bts_zip=bts_zip, **kwargs)
    img = draw_bytes_as_image(bts=bts_zip, **kwargs)
    img_save(img=img, **kwargs, path=path)


# EXPORTED FUNCTIONS

def zip(path: str,
        scale: int = 1,
        color_mode: str = 'heat'):
    """
    Encrypt (zip) chosen file or whole directory into a single image file.
    :param path: Path to a single file or whole directory to "zip". Can be absolute or relative.
    :param scale: Scale of output image file. Default: 1;
    :param color_mode: Color mode of output image file.
    Available color_mode's are: "bw", "heat", "heat_toxic", "rainbow", "red", "blue".
    Default: "heat".
    """

    color_mode = color_mode.lower()

    encrypt_hub(path=path, scale=scale, color_mode=color_mode)


def unzip(path: str,
          scale: int = 1,
          color_mode: str = 'heat'):
    """
    Decrypt (unzip) files from an image file.
    :param path: Path to an image file to "unzip". Can be absolute or relative.
    :param scale: Scale of input image file. Default: 1;
    :param color_mode: Color mode of input image file.
    Available color_mode's are: "bw", "heat", "heat_toxic", "rainbow", "red", "blue".
    Default: "heat".
    """
    if os.path.isdir(path):
        file_chosen = False
    else:
        file_chosen = True

    color_mode = color_mode.lower()

    decrypt_image(path=path, scale=scale, color_mode=color_mode, file_chosen=file_chosen)
