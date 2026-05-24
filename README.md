[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5NorvP5a)

# Perspective transformation
- Install the required packages from [`requirements.txt`](requirements.txt)
- Run [`image_extractor.py`](./perspective_transformation/image_extractor.py) located in [`perspective_transformation`](./perspective_transformation/) via command line 
- Use the following command line parameters for specification of input file, output destination, output file name and resolution

|flag|parameter|required?|default|
|----|---------|---------|-------|
|`--input`| input file (image) | no | `sample_image.jpg` |
|`--outdir`| output destination (directory) | no | `./extracted/` | 
|`--name`| name of the output file (warped image) | no | input file name + `_extracted`|
|`--out_width`| target width for the warped output image | yes | - |
|`--out_height`| target height for the warped output image | yes | - |

- example with minimum parameters: `python .\image_extractor.py --out_width 750 --out_height 500` 
 ( you need to move to  [`perspective_transformation`](./perspective_transformation/) if you want to use the default image)
- example with all options/parameters: `python .\image_extractor.py --input .\sample_image.jpg --name result  --outdir results --out_width 750 --out_height 500`

- When the program is running you can click in the `Preview Window` to select four points in the image to have a region to extract from
- After you select four points the `Result Window` will open so you can view the warped image
- When the `Resut Window` is open you can press `s` to save the result as an image file (same file type as input file).
- You can press `ESC` to discard all your selected points (and if four points are selected the warped image) so you can restart selecting points
- Press `q` to exit the program