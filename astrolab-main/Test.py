"""

Testing file for the variable galaxy counter.
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.modeling.models import Gaussian2D
from astropy.modeling import models
import GalaxyCounter as gal
from astropy.visualization import ZScaleInterval
from astropy.nddata import Cutout2D

#%%
# Testing variable and fixed aperatures on separate regions of the full image

sky_data = gal.openccd("starsmasked.fits") # Ensure the datafile is saved (astrolab file)
interval = ZScaleInterval()

def imagetaker(arr, indices, size = (400, 600)):
    '''
    Plots a given region of the sky and returns the data for the section.
    Args:
        arr:: array
            array of the image data
        indices:: list
            centrale coordinates of image section
        size:: size of image
    Returns:
        subsection of full image for given size and coordinates
        
        
    '''
    
    subsectioncenter = (indices[1], indices[0])
    size = size
    subsection = Cutout2D(arr, subsectioncenter, size)
    interval = ZScaleInterval()
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title("Test region cutout")
    ax.set_xlabel('relative x coordinates (+' + str(indices[1]) + ")")
    ax.set_ylabel('relative y coordinates (+' + str(indices[0]) + ")")
    im = ax.imshow(interval(subsection.data), origin='lower')
    plt.show()
    
    return subsection


region1 = imagetaker(sky_data, [1161, 1956])
region2 = imagetaker(sky_data, [1279, 474])
"""
fixed_test = gal.fixed_aperture(region1.data, 3418, 20)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_title("Test region cutout")
ax.set_xlabel('relative x coordinates')
ax.set_ylabel('relative y coordinates')
im = ax.imshow(interval(fixed_test.data), origin='lower')
plt.show()
"""

#%%
# testing the variable counter on 2 subsections of the full image
sourcelim = 3500    # Galaxy identification limit
radiuslim = 3443    # Masking radius limit
minsize = 2 # initialise mininimum size of galaxy identification easy to change for testing
galaxyvals, galaxylocales, galaxyfluxes, centers, maskedregion = gal.var_aperture(region1.data, sourcelim, radiuslim, True, minsize)
centerx = [] #Compiling x coordinates of center pixels
centery = [] #Compiling y coordinates of center pixels
for coord in centers:
    centerx.append(coord[1])
    centery.append(coord[0])

interval = ZScaleInterval()
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_title("Test region cutout")
ax.set_xlabel('relative x coordinates (+1956)')
ax.set_ylabel('relative y coordinates (+1161)')
im = ax.imshow(interval(maskedregion), origin='lower')
plt.scatter(centerx, centery, color="r") # plots the centerpoint of each galaxy detected on the graph
plt.show()

galaxyvals2, galaxylocales2, galaxyfluxes2, centers2, maskedregion2 = gal.var_aperture(region2.data, sourcelim, radiuslim, True, minsize)
centerx2 = [] #Compiling x coordinates of center pixels
centery2 = [] #Compiling y coordinates of center pixels
for coord in centers2:
    centerx2.append(coord[1])
    centery2.append(coord[0])

interval = ZScaleInterval()
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_title("Test region cutout")
ax.set_xlabel('relative x coordinates (+474)')
ax.set_ylabel('relative y coordinates (+1279)')
im = ax.imshow(interval(maskedregion2), origin='lower')
plt.scatter(centerx2, centery2, color="r") # plots the centerpoint of each galaxy detected on the graph
plt.show()

#%%
# Testing variable counter using 2D Gaussian model for a galaxy on a simulated sky

    
imshape = (500, 500)
y, x = np.indices(imshape) # Creating the meshgrid

np.random.seed(1) # Seeding the random number generator, different seeds will create different skies
    
N = 500
model_params = [
    dict(amplitude=np.random.uniform(3500, 10000), 
         x_mean=np.random.uniform(0, imshape[1] - 1), # Mean value of the simulated galaxy
         y_mean=np.random.uniform(0, imshape[0] - 1),
         x_stddev=np.random.uniform(1, 5),  # Randomising std of 2D Guassian 
         y_stddev=np.random.uniform(1, 5),
         theta=np.random.uniform(0, 2 * np.pi)) # Rotation angle in radians
    
    for _ in range(N)]
    
    
model_list = [models.Gaussian2D(**kwargs) for kwargs in model_params]

full_image = np.ones(imshape) * 3420

for model in model_list:
    model.bounding_box = None
    model.render(full_image)
    

flux = full_image.sum() # Calculating the total flux from the sources

# Full model image

plt.figure()
plt.imshow(full_image, origin='lower')
plt.xlabel('x coordinates')
plt.ylabel('y coordinates')
plt.title('Simulated sky with N = 500 Sources')
plt.colorbar()





