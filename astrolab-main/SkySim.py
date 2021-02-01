from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.modeling.models import Gaussian2D
from astropy.modeling import models
from time import time
import GalaxyCounter as gal

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


