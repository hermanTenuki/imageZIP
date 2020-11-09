from PIL import Image
import io as io
import os
import math


def _calculate_color(num: int, color_mode: str):
    if color_mode == 'bw':
        return num
    elif color_mode == 'heat_map':
        # original num is always be 0 >= num <= 255 (it's actually 256 different bytes)
        # by multiplying num, we are getting wider range of colors
        num *= 4
        # all pallets multiplied and divided by num should be equal 256 to store right amount of data
        # palettes is a ranges of colors to store data in
        palette1 = 256
        # color_min and color_max is a color range of palette1
        # Don't forget that 0 counts, so full range from color_min to color_max is 256, not 255
        color_min = 0

    elif color_mode == 'heat_map_better':
        num *= int(3.5)
        palette1 = 224
        color_min = 0

    else:
        raise AttributeError(f'"{color_mode}" color_mode does not exist.')

    color_max = color_min + palette1 - 1
    palette2 = palette1 * 2
    palette3 = palette2 + palette1
    palette4 = palette3 + palette1

    if num <= palette1:
        return color_min, color_min + num, color_max
    elif num <= palette2:
        num -= palette1
        return color_min, color_max, color_max - num
    elif num <= palette3:
        num -= palette2
        return color_min + num, color_max, color_min
    elif num <= palette4:
        num -= palette3
        return color_max, color_max - num, color_min


def _calculate_sizes(multiplier, perimeter):
    while multiplier > 0:
        a = perimeter / multiplier
        if a % 1 == 0:
            b = perimeter / a
            return int(min([a, b])), int(max([a, b]))
        multiplier -= 1


def draw_bytes_on_image(bts, color_mode, scale):
    bts_len = len(bts)
    bt_index = 0

    size_original = math.ceil(math.sqrt(bts_len))
    size_x, size_y = _calculate_sizes(size_original, bts_len)
    if color_mode == 'bw':
        color_PIL = 'L'
    else:
        color_PIL = 'RGB'
    img = Image.new(color_PIL, (size_x * scale, size_y * scale), color='white')

    for row in range(size_y):
        for col in range(size_x):
            try:
                color = _calculate_color(num=bts[bt_index], color_mode=color_mode)
            except IndexError:
                break
            x, y = col * scale, row * scale
            for i in range(scale):
                for j in range(scale):
                    img.putpixel((x + j, y + i), color)
            bt_index += 1
    return img


def _encrypt_save(overwrite, path, img):
    if overwrite:
        os.remove(path)
    img.save(path + '.png')


def encrypt_file(**kwargs):
    path = kwargs['path']
    scale = kwargs['scale']
    mode = kwargs['crypt_mode']
    overwrite = kwargs['overwrite']
    color_mode = kwargs['color_mode']

    with open(path, 'rb') as file:
        bts = file.read()

    if mode == 'normal':
        img = draw_bytes_on_image(bts, color_mode, scale)
        _encrypt_save(overwrite, path, img)
    elif mode == 'zip':
        print(path)
    else:
        raise AttributeError('Mode is not defined.')


def decrypt_file(**kwargs):
    path = kwargs['path']
    scale = kwargs['scale']
    overwrite = kwargs['overwrite']
    color_mode = kwargs['color_mode']

    with open(path, 'rb') as file:
        image = file.read()
    image = Image.open(io.BytesIO(image))

    bytesDict = {}
    for i in range(256):
        bytesDict[str(_calculate_color(i, color_mode=color_mode))] = bytes([i])

    bts = []

    for row in range(int(image.height / scale)):
        for col in range(int(image.width / scale)):
            try:
                bts.append(bytesDict[str(image.getpixel((col * scale, row * scale)))])
            except KeyError:
                raise RuntimeError("Can't decode an image, settings can be incorrect or image is distorted.")

    original_path, _ = os.path.splitext(path)
    if overwrite:
        file = open(original_path, 'wb')
    else:
        without_extension, extension = os.path.splitext(original_path)
        file = open(without_extension + '_decrypted' + extension, 'wb')
    file.writelines(bts)
    file.close()


def _crypt_with_mode(mode, **kwargs):
    if mode == 'encrypt':
        return encrypt_file(**kwargs)
    elif mode == 'decrypt':
        decrypt_file(**kwargs)
    else:
        raise AttributeError('imageCrypt mode is not defined.')


def crypt(path, bts_zip, crypt_mode, **kwargs):
    if os.path.isdir(path):
        for name in os.listdir(path):
            path_to_name = os.path.join(path, name)
            if os.path.isfile(path_to_name) or crypt_mode == 'zip':
                res = _crypt_with_mode(path=path_to_name, crypt_mode=crypt_mode, **kwargs)
                if crypt_mode == 'zip':
                    bts_zip.append(res)
            else:
                crypt(path_to_name, **kwargs)  # Recursion to inner folders
    else:
        _crypt_with_mode(path=path, crypt_mode=crypt_mode, **kwargs)


def encrypt(path: str,
            scale: int = 1,
            mode: str = 'zip',
            overwrite: bool = False,
            color_mode: str = 'heat_map'):
    """
    Encrypt a file or whole directories into an image file.
    :param path: Path to a file or directory.
    :param scale: Scale of output image. Increase for more clear image. Default: 1.
    :param mode: Encryption mode. "zip" is for archiving files and whole directories to one image file.
    This image file will store all the folders, files data, their names and relative locations.
    "normal" mode is for encrypting only file's data, if directory is specified, it will encrypt all files inside it,
    including all the inner directories files, but folders itself will stay the same.
    :param overwrite: Overwrite original file with encrypted image file or create a new image file with the same folder
    as original. Default: False.
    :param color_mode: Color mode of output image. Default: "heat_map".
    :param enforce_compact: If image can't be built as square or a rectangle, but only single line,
    it will build as square with some empty bytes at the end as white color (except "bw" mode).
    You can enforce it to be compact in any case. Default: False.
    """
    bts_zip = []
    crypt(path=path,
          mode='encrypt',
          scale=scale,
          crypt_mode=mode,
          overwrite=overwrite,
          color_mode=color_mode,
          bts_zip=bts_zip)
    print(path)
    _encrypt_save(overwrite, path, draw_bytes_on_image(bts_zip, scale=scale, color_mode=color_mode))


def decrypt(path: str,
            scale: int = None,
            mode: str = 'zip',
            overwrite: bool = False,
            color_mode: str = None):
    """
    Decrypt an image file or whole directories image files into an original file.
    :param path: Path to a file or directory. If directory is specified, it will decrypt all files inside it,
    including all the inner directories files.
    :param scale: Scale of input image. It's important to specify original scale.
    If scale is not specified, decryptor will try to find out original scale on it's own. Default: None.
    :param mode: Decryption mode. "zip" is for archiving files and whole directories to one image file.
    This image file is storing all the folders, files data, their names and relative locations.
    "normal" mode is for decrypting only file's data, if directory is specified, it will decrypt all files inside it,
    including all the inner directories files, but folders itself will stay the same.
    :param overwrite: Overwrite encrypted image file with decrypted original file or create a new original file in
    the same folder. Default: False.
    :param color_mode: Color mode of input image. It is also important to specify original color_mode.
    If color_mode is not specified, decryptor will try to find out original color_mode on it's own. Default: None.
    """
    crypt(path=path,
          mode='decrypt',
          scale=scale,
          crypt_mode=mode,
          overwrite=overwrite,
          color_mode=color_mode,
          bts_zip=[])
