# This is the folder of Leonardo Bossi and Joseph bWang's code on astronomical image processing.

There should be four files:
	mosaic.fits
	GalaxyCounter.py
	analysis.py
	SkySim.py

In order: 
mosaic.fits contains the image data that we intend to analyse, 
GalaxyCounter.py contains all the functions used to extract usable data from the image: how many galaxies, where, of what overall measured brightness
analysis.py is the file which calls on GalaxyCounter to get the data< and analyses the image
SkySim.py is a test file that generates a simulated sky with random Gaussian light sources on which to test the code of GalaxyCounter before its use on the image proper.
