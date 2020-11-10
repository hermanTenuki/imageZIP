# imageZIP

This is a small python package to archive (encrypt) files and directories into a single image file. 

This project is made just for fun, it has no practical use, output "ZIP" image will always have the same or greater file size than it's content. Also, this is not easy-to-scan like QR codes.

Algorithm is pretty easy. If folder to zip is chosen, it will iterate through all folders and files inside it. If folder is found, it will write relative path of folder in bytes and add special folder delimiter at the end. If file is found, it will write it's relative path and name in bytes, add special file delimiter and then write all it's content in bytes with additional second file delimiter. When bytes array is ready to go, it will build an image, where individual pixels representing particular byte number.

## Example

![demo image](.github/demo_zip.png)

This is an "imageZIP archive", containing this whole "imageZIP" repository.
 
It was created with ```imageZIP.zip("imageZIP", scale=4)```.

You can actually download this image and unzip it with ```imageZIP.unzip("demo_zip.png", scale=4)```, it will create "imageZIP" folder with all repository files.

## How to use

To download this package, you can use ```pip install imageZIP```.

Then go to python terminal and write ```import imageZIP```.

Then you can use 2 available functions:

- ```imageZIP.zip(path: str, scale: int = 1, color_mode: str = 'heat_map')```;
- ```imageZIP.unzip(path: str, scale: int = 1, color_mode: str = 'heat_map')```.

Only ```path``` attribute is necessary here, other settings can be omitted.

#### Notes:

- For ```zip``` and ```unzip``` you have to provide same ```scale``` and ```color_mode``` settings;
- ```scale``` is have to be ```int > 0```;
- Available ```color_mode```s are: ```bw```, ```heat_map```, ```heat_map_toxic```;
- For now, absolute paths for linux and mac are not tested, but it should work.
