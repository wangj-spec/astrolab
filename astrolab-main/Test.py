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

# Plotting the full image

interval = ZScaleInterval()

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_title("Full image with blooming and noise masked")
ax.set_xlabel('relative x coordinates')
ax.set_ylabel('relative y coordinates')
im = ax.imshow(interval(sky_data), origin='lower')
cbar = fig.colorbar(im)
plt.show()


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


#%%
# testing the variable counter on 2 subsections of the full image by plotting
# the centres to see where the galaxies are being detected.

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
ax.set_title("Test region cutout centred about (1956,1161)")
ax.set_xlabel('relative x coordinates (+1656)')
ax.set_ylabel('relative y coordinates (+961)')
im = ax.imshow(interval(maskedregion), origin='lower')

plt.scatter(centerx, centery, color="k") # plots the centerpoint of each galaxy detected on the graph
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
ax.set_title("Test region cutout centred about (474,1279")
ax.set_xlabel('relative x coordinates (+274)')
ax.set_ylabel('relative y coordinates (+979)')
im = ax.imshow(interval(maskedregion2), origin='lower')

plt.scatter(centerx2, centery2, color="k") # plots the centerpoint of each galaxy detected on the graph
plt.show()

print('Total number of galaxies found in region 1 = '+str(len(centerx)))
print('Total number of galaxies found in region 2 = '+str(len(centerx2)))

#%%
# Using a lower galaxy detection limit
lim_lower = 3460

sky_data = gal.openccd("starsmasked.fits")
region1 = imagetaker(sky_data, [1161, 1956])

lowerlim_test1 = gal.var_aperture(region1.data, lim_lower, radiuslim, True, minsize)

centerx3 = [] #Compiling x coordinates of center pixels
centery3 = [] #Compiling y coordinates of center pixels

for coord in lowerlim_test1[3]:
    centerx3.append(coord[1])
    centery3.append(coord[0])
    
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)    
ax.set_title("Test region 1 plotted with source detection limit of p = 3460")
ax.set_xlabel('relative x coordinates (+1656)')
ax.set_ylabel('relative y coordinates (+961)')
im = ax.imshow(interval(lowerlim_test1[4]), origin='lower')

plt.scatter(centerx3, centery3, color="k") # plots the centerpoint of each galaxy detected on the graph
plt.show()

#%%

# Using differnet radius masking limits on subsections of the image
sky_data = gal.openccd("starsmasked.fits")
region1 = imagetaker(sky_data, [1161, 1956])
region2 = imagetaker(sky_data, [1279, 474])

sourcelim = 3500
radiuslim = 3443 
radiuslim_high = 3500
radiuslim_low  = 3400 

# Testing low masking radius
lowrad_test = gal.var_aperture(region2.data, sourcelim, radiuslim_low)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)    
ax.set_title("Test region 2 plotted with radius masking limit of p = 3400")
ax.set_xlabel('relative x coordinates (+274)')
ax.set_ylabel('relative y coordinates (+979)')
im = ax.imshow(interval(lowrad_test[3]), origin='lower')

# It is evident that the radii are too big and will mask out other galaxies, as 
# well as produce inaccurate flux results


# Testing high masking radius, we see that the outer regions of the galaxies have
# not been masked out.

highrad_test = gal.var_aperture(region1.data, sourcelim, radiuslim_high)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)    
ax.set_title("Test region 1 plotted with radius masking limit of p = 3480")
ax.set_xlabel('relative x coordinates (+1656)')
ax.set_ylabel('relative y coordinates (+961)')
im = ax.imshow(interval(highrad_test[3]), origin='lower')




#%%
# Testing variable counter using 2D Gaussian model for a galaxy on a simulated sky
    
imshape = (500, 500)
y, x = np.indices(imshape) # Creating the meshgrid

np.random.seed(1) # Seeding the random number generator, different seeds will create different skies

# Setting the number of randomly generated galaxies to 500    
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

# Setting the background flux value to 3420
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
plt.colorbar(label = 'Pixel brightness value')
plt.legend()

# Running the variable aperature on the image
test_gaussian = gal.var_aperture(full_image, 3500, 3470, False, 2)

# Plot of the simulated image masked out
plt.figure()
plt.imshow(test_gaussian[3], origin='lower')
plt.xlabel('x coordinates')
plt.ylabel('y coordinates')
plt.title('Simulated sky with N = 500 Sources')
plt.colorbar(label = 'Pixel brightness value')
plt.legend()

# The total flux from the simulated galaxies (subtacting the background values)
real_flux = flux - (500 * 500 * 3420)


print('total number of galaxies found using a variable aperature = '+str(len(test_gaussian[0])))
print('simulated flux = '+str(real_flux))
print('flux found using variable aperature = '+str(np.nansum(test_gaussian[2])))
print('total error in flux calculation = 8.77%')

#%%
# Testing variable aperture and fixed aperture for one simluated galaxy.

imshape2 = (50, 50)

y, x = np.indices(imshape2) # Creating the meshgrid

np.random.seed(7) # Seeding the random number generator, different seeds will create different skies

# Setting the number of randomly generated galaxies to 500    
N = 1
model_params = [
    dict(amplitude=np.random.uniform(8000, 10000), 
         x_mean=np.random.uniform(24.5, 25.5), # Mean value of the simulated galaxy
         y_mean=np.random.uniform(24.5, 25.5),
         x_stddev=np.random.uniform(6, 6.5),  # Randomising std of 2D Guassian 
         y_stddev=np.random.uniform(6, 6.5),
         theta=np.random.uniform(0, 2 * np.pi)) # Rotation angle in radians
    
    for _ in range(N)]
    
    
model_list = [models.Gaussian2D(**kwargs) for kwargs in model_params]

# Setting the background flux value to 3420
one_galaxy = np.ones(imshape2) * 3420

for model in model_list:
    model.bounding_box = None
    model.render(one_galaxy)

plt.figure()
plt.imshow(one_galaxy, origin='lower')
plt.xlabel('x coordinates')
plt.ylabel('y coordinates')
plt.title('Simulated galaxy')
plt.colorbar(label = 'Pixel brightness value')
plt.legend()

fixedap_test = gal.fixed_aperture(one_galaxy, 3500, 7)

plt.figure()
plt.imshow(fixedap_test[3], origin='lower')
plt.xlabel('x coordinates')
plt.ylabel('y coordinates')
plt.title('Simulated galaxy masked with fixed aperture')
plt.colorbar(label = 'Pixel brightness value')
plt.legend()

print('Total number of galaxies detected for fixed aperature method = '+str(len(fixedap_test[0])))


#Using variable aperature
varap_test = gal.var_aperture(one_galaxy, 3500, 3450)

plt.figure()
plt.imshow(varap_test[3], origin='lower')
plt.xlabel('x coordinates')
plt.ylabel('y coordinates')
plt.title('Simulated galaxy masked with variable aperture')
plt.colorbar(label = 'Pixel brightness value')
plt.legend()

print('Variable aperture finds '+str((len(varap_test[0])))+ ' galaxy, as expected')





