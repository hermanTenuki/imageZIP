from imageZIP import imageZIP
import unittest
import os
import shutil


class TestBehavior(unittest.TestCase):
    def test_file(self):
        original_file_name = 'tests/test file ☆.txt'
        zip_path = 'tests/test file ☆.txt_zip.png'
        with open(original_file_name, 'r', encoding='UTF-8') as file:
            original_file = file.read()

        imageZIP.zip(original_file_name)
        self.assertTrue(os.path.exists(zip_path))
        self.assertFalse(os.path.exists('test file ☆.txt_zip.png'))

        os.remove(original_file_name)

        imageZIP.unzip(zip_path)
        with open(original_file_name, 'r', encoding='UTF-8') as file:
            unzipped_file = file.read()
        self.assertTrue(os.path.exists(original_file_name))
        self.assertEqual(unzipped_file, original_file)

        os.remove(zip_path)

    def test_blank_file(self):
        original_file_name = 'tests/test folder/0'
        zip_path = 'tests/test folder/0_zip.png'
        with open(original_file_name, 'r', encoding='UTF-8') as file:
            original_file = file.read()

        imageZIP.zip(original_file_name)
        self.assertTrue(os.path.exists(zip_path))
        self.assertFalse(os.path.exists('0_zip.png'))

        os.remove(original_file_name)

        imageZIP.unzip(zip_path)
        with open(original_file_name, 'r', encoding='UTF-8') as file:
            unzipped_file = file.read()
        self.assertTrue(os.path.exists(original_file_name))
        self.assertEqual(unzipped_file, original_file)

        os.remove(zip_path)

    def test_binary_file(self):
        original_file_name = 'tests/test folder/inner folder/image.jpg'
        zip_path = 'tests/test folder/inner folder/image.jpg_zip.png'
        with open(original_file_name, 'rb') as file:
            original_file = file.read()

        imageZIP.zip(original_file_name)
        self.assertTrue(os.path.exists(zip_path))
        self.assertFalse(os.path.exists('image.jpg_zip.png'))

        os.remove(original_file_name)

        imageZIP.unzip(zip_path)
        with open(original_file_name, 'rb') as file:
            unzipped_file = file.read()
        self.assertTrue(os.path.exists(original_file_name))
        self.assertEqual(unzipped_file, original_file)

        os.remove(zip_path)

    def test_folder(self):
        original_folder_name = 'tests/test folder/'
        zip_path = 'tests/test folder_zip.png'
        path_empty_file = os.path.join(original_folder_name, '0')
        with open(path_empty_file, 'rb') as file:
            empty_file = file.read()
        path_image_file = os.path.join(original_folder_name, 'inner folder/image.jpg')
        with open(path_image_file, 'rb') as file:
            image_file = file.read()

        imageZIP.zip(original_folder_name)
        self.assertTrue(os.path.exists(zip_path))
        self.assertFalse(os.path.exists('test folder_zip.png'))

        shutil.rmtree(original_folder_name, ignore_errors=True)

        imageZIP.unzip(zip_path)
        with open(path_empty_file, 'rb') as file:
            empty_file_new = file.read()
        self.assertEqual(empty_file_new, empty_file)
        with open(path_image_file, 'rb') as file:
            image_file_new = file.read()
        self.assertEqual(image_file_new, image_file)

        os.remove(zip_path)

    def test_abs_path_folder(self):
        if os.name == 'nt':
            os.mkdir('C:/test_imageZIP')
            os.mkdir('C:/test_imageZIP/test folder/')
            original_folder_name = 'C:/test_imageZIP/test folder/'
            zip_path = 'C:/test_imageZIP/test folder_zip.png'
        else:
            os.mkdir('/test_imageZIP/')
            os.mkdir('/test_imageZIP/test folder/')
            original_folder_name = '/test_imageZIP/test folder/'
            zip_path = '/test_imageZIP/test folder_zip.png'
        path_file = os.path.join(original_folder_name, '0')
        with open(path_file, 'w') as file:
            file.write('testing 123')
        with open(path_file, 'rb') as file:
            text_file = file.read()

        imageZIP.zip(original_folder_name)
        self.assertTrue(os.path.exists(zip_path))
        self.assertFalse(os.path.exists('test folder_zip.png'))

        if os.name == 'nt':
            shutil.rmtree(original_folder_name, ignore_errors=True)
        else:
            shutil.rmtree(original_folder_name, ignore_errors=True)

        imageZIP.unzip(zip_path)
        with open(path_file, 'rb') as file:
            text_file_new = file.read()
        self.assertEqual(text_file_new, text_file)

        if os.name == 'nt':
            shutil.rmtree('C:/test_imageZIP', ignore_errors=True)
        else:
            shutil.rmtree('/test_imageZIP/', ignore_errors=True)


class TestSettings(unittest.TestCase):
    def _test_with_settings(self, *args, **kwargs):
        original_file_name = 'tests/test file ☆.txt'
        zip_path = 'tests/test file ☆.txt_zip.png'
        with open(original_file_name, 'r', encoding='UTF-8') as file:
            original_file = file.read()

        imageZIP.zip(original_file_name, *args, **kwargs)
        self.assertTrue(os.path.exists(zip_path))
        self.assertFalse(os.path.exists('test file ☆.txt_zip.png'))

        os.remove(original_file_name)

        imageZIP.unzip(zip_path, *args, **kwargs)
        with open(original_file_name, 'r', encoding='UTF-8') as file:
            unzipped_file = file.read()
        self.assertTrue(os.path.exists(original_file_name))
        self.assertEqual(unzipped_file, original_file)

        os.remove(zip_path)

    def test_scale(self):
        with self.assertRaises(SystemError):
            self._test_with_settings(scale=0)
        with self.assertRaises(TypeError):
            self._test_with_settings(scale=1.2)
        self._test_with_settings(scale=8)

    def test_colors(self):
        with self.assertRaises(AttributeError):
            self._test_with_settings(color_mode='random123123')
        self._test_with_settings(color_mode='bw')
        self._test_with_settings(color_mode='heat_map')
        self._test_with_settings(color_mode='heat_map_toxic')


if __name__ == '__main__':
    # imageZIP.unzip('tests/test folder_zip.png')
    unittest.main()
