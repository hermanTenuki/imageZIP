from setuptools import setup
import imageZIP

with open("README.md", "r") as file:
    long_description = file.read()

setup(name='imageZIP',
      version=imageZIP.__version__,
      description='Archive (encrypt) files and directories to image file',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/hermanTenuki/imageZIP/',
      author=imageZIP.__author__,
      author_email=imageZIP.__email__,
      license=imageZIP.__license__,
      packages=['imageZIP'],
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: Implementation :: CPython',
            'Operating System :: OS Independent',
            'Topic :: Scientific/Engineering :: Image Processing',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Security :: Cryptography'
      ],
      include_package_data=False,
      install_requires=['Pillow'],
      python_requires='>=3')
