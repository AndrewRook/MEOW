#MEOW

MEOW (Measuring Enamel Occlusal Wear) is a program designed to semi-automate the estimation of wear patterns on fossil teeth. Under the hood it uses the watershed segmentation algorithm from the powerful OpenCV library, and presents an accessible interface so the user can help guide the algorithm by selecting image regions belonging to background, enamel, and dentin. All control is done graphically via mouse or keyboard commands, allowing for efficient analysis of large sets of images.

###Pre-requisites:
* Python 2.7 (may also work on other versions)
* Numpy
* OpenCV, with python bindings.

##Windows installation instructions:
1. [Download Python 2.7.9](https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi), then double-click the installer and follow prompts to install. **Note**: the rest of these instructions assume that you install Python into the default directory; if you choose to install to a non-default directory, you'll need to modify some of the filepaths.
2. Set your computer's Path variable:
   1. Open the "Control Panel" (you can search for it).
   2. Click on "System".
   3. Select "Advanced System Settings".
   4. Select "Environment Variables".
   5. In the User Variables section, Either create a Path variable with the following or append it to an existing Path variable: <br\> `C:\Python27;C:\Python27\Lib\site-packages\;C:\Python27\Scripts\;`
3. Confirm the successful installation by opening the command prompt (search for "cmd"), then entering `python`. The Python interpreter should load, giving you a `>>>` prompt rather than the usual `C:\>`. 
4. [Download Numpy 1.9.2](http://sourceforge.net/projects/numpy/files/NumPy/1.9.2/numpy-1.9.2-win32-superpack-python2.7.exe/download), then double click the installer and follow the prompts.
5. Confirm successful installation by starting a new instance of the command prompt, entering `python`, then entering `import numpy as np; np.__version__`. You should see `1.9.2` printed to the screen.
6. [Download OpenCV](http://sourceforge.net/projects/opencvlibrary/files/opencv-win/3.0.0/opencv-3.0.0.exe/download), then double click to extract the package.
7. Go to `opencv\build\python\2.7\x86\`, and copy the `cv2.pyd` file to `C:\Python27\Lib\site-packages\`.
8. Confirm successful installation by starting a new instance of the command prompt, entering `python`, then entering `import cv2; cv2.__version__`. You should see `3.0.0` printed to the screen.
9. Click the "Download ZIP" button on the right side of this page. Choose a download location, then double click on the downloaded file to unzip it.
10. Open up a new command prompt, then navigate to the `example\` folder in the unzipped MEOW folder (e.g. `cd C:\Users\AndrewRook\MEOW-master\MEOW-master\example\`).
11. Run the following command: `python ../MEOW.py example_teeth_input_list.txt test_output.txt`. If you don't see any errors and a bunch of windows pop up, congrats! You've successfully installed MEOW.

##Operating Instructions:
The general calling syntax for MEOW is as follows:

```bash
python MEOW.py [file with list of image names] [output filename]
```

The first argument should be a filename that has a single-column list of image names, like so:
```
img_0001.jpg
img_0002.jpg
...
```

(NOTE: If you images are in a different folder than the `MEOW.py` script, you'll need to include the full file paths.)

The second argument gives the filename that the output measurements will go into. THIS WILL SILENTLY OVERWRITE ANY EXISTING FILE BY THAT NAME, so be careful!

Once the program is running, it will iterate through the image list one by one. First it will show the original image, and prompt you to choose a region of interest (ROI). Select this region by left-clicking and dragging on the image. Once you release the mouse a new image window will pop up showing a zoomed in view of the ROI. You can reselect the ROI at any time via this procedure, but be aware that it will erase any progress you've made on that image.

From this point you'll be operating on the ROI image window. There are several available options here:

* ESC -- Move onto the next image without saving anything.
* q -- Save and move on. Only works after a segmentation image has been made.
* s -- Switch to segmentation mode.
* t -- Switch to tooth identification mode.
* [space] -- Make the segmentation.

There are two major modes, segmentation mode and tooth identification mode, with different options for each:

####Tooth ID mode:
* left-click and drag -- draw a rectangle around a tooth. This rectangle doesn't have to be perfect as long as it doesn't overlap any other teeth (the program ignores background regions when computing areas, so don't worry about that!).
* d -- Delete the nearest tooth identification.
* l (lowercase L, not an i)-- Label the nearest tooth. After clicking l, just type out a label (e.g. m2,p1,m?) and then hit enter. The label will display in the terminal as you enter it. Accepted characters are a-z,A-Z,0-9, and ?. Delete works as well. The label will be writting on both the diagnostic plot and in the output file. If no label is specified, the relative position of the tooth will be used as the label instead (e.g. 1 for the leftmost tooth, 2 for the next tooth over, etc). 
* z -- Delete all tooth identifications.

####Segmentation mode:
* left-click and drag -- draw markers to help guide the segmentation process.
* 1-4 -- change the marker type. 1 = background (green), 2 = enamel (red), 3 = dentin (yellow), 4 = not sure (pink).
* z -- Delete all markers.

The basic workflow is to identify the teeth you want to measure, then make a few marks to identify the general background, enamel, and dentin regions. Next, run the watershed segmentation with [space], which pops up a new window showing the ROI overlaid with the algorithm's current guess at the segmentation. From there, go back to the ROI and add markers where necessary to improve the segmentation. When you're happy with it, press 'q'. This will save a diagnostic image (with the filename of the original image + the extension "_segmented" added) and print out the areas of each marker to the text file specified on the command line. Note that these areas are in units of pixels of the ORIGINAL (not the ROI) image. The tooth id in this file is the same as the number printed above all the teeth in the diagnostic image.
