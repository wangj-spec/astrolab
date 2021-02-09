# This is the folder of Leonardo Bossi and Joseph Wang's code on astronomical image processing.

Python version used: 3.7.6
Libraries used in code: Matplotlib, Numpy, Astropy.

There should be four files:
	mosaic.fits
	GalaxyCounter.py
	analysis.py
	Test.py

mosaic.fits is a FITS file containing the image data that we intend to analyse.

GalaxyCounter.py 
Contains all the functions used to extract usable data from the image. Importantly, the file begins with the coordinates of the stars/blooming noise we want to mask out BEFORE the main analysis. 

This module includes the variable aperture galaxy counter, which is what is used for the main analysis.

analysis.py
Module begins by using coordinates for stars and blooming in GalaxyCounter.py and masking them. Running this file will automatically save a new FITS file "starsmasked.fits" which is the masked image that is ready to be analysed. 

Module calls on GalaxyCounter and is where all the analysis of the image, as well as the number count plots and uncertainties are derived.

Test.py 
Where the testing of the algorithm is carried out. This includes testing in two regions from the full image (in areas with different background values), as well as testing on a simulated image with 2D Gaussians representing galaxies.
