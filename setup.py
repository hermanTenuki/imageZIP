from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(name='imageZIP',
      version='3',
      description='Archive (encrypt) files and directories to image file',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/hermanTenuki/imageZIP/',
      author='Herman Schechkin (hermanTenuki)',
      author_email='itseasy322@gmail.com',
      license='MIT',
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
