from astropy.io import fits
import scipy as sp
import matplotlib.pyplot as plt

hdulist = fits.open("mosaic.fits")
hdulist.info()
data = hdulist[0].data
print(data)

starcoords = [[(2144,3182),(2124,3710)],\
              [(2453,3441),(1474,3384)],\
              [(2079,1452),(2097,1405)],\
              [(2099,1449),(2080,1402)],\
              [(1447,4048),(1454,4019)],\
              [(2153,3348),(2313,3231)],\
              [(1369,3283),(1513,3141)],\
              [(1410,3165),(1462,2966)],\
              [(1421,2967),(1454,0)],\
              [(1176,446),(1607,425)],\
              [(1463,488),(1399,144)],\
              [(1077,340),(1716,306)],\
              [(2427,417),(2570,0)],\
              [(2570,4611),(2479,417)],\
              [(721, 3417),(832,3194)],\
              [(852, 2361),(952,2206)],\
              [(925, 2833),(1026,2694)],\ 
              [(530, 4128),(597,4061)],\
              [(1425, 4006),(1492,3997)],\
              [(1416, 4506),(1474,3450)],\
              [(0, 4611), (137,0)],\
              [(0,0), (2569, 140)],\
              [(2099, 4611), (2570, 4388)], [(0, 4611), (2570, 4499)]]


data1d = data.flatten()
print(data1d)

data1dmod = data1d[data1d > 4000]
plt.hist(data1dmod, bins = 1000)
plt.show()

subsectioncenter = (781,1478) #coordinates of center of subsection to look at 
size = (398, 614) #shape around center of subsection to look at, of form (y dimension, x dimension)
subsection = Cutout2D(data, subsectioncenter, size)

interval = ZScaleInterval() #viewing in Zscale

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_title("Subsection of sky, origin at (474,1279), galaxies down to 3468")
ax.set_xlabel('relative x coordinates (+474)')
ax.set_ylabel('relative y coordinates (+1279)')

im = ax.imshow(interval(subsection.data), origin='lower') #plotting of image
plt.show()

hdulist.close()


starcoords2 = [[(721, 3417), (832, 3194)], [(852, 2361), (952, 2206)], \
               [(925, 2833),(1026, 2694)], [(530, 4128), (597, 4061)], \
                [(1425, 4006) ,(1492, 3997)] , [(1416, 4506),(1474, 3450)],\
                [(0, 4611), (137, 0)], [(0,0), (2569, 140)], \
                        [(2099, 4611), (2570, 4388)], [(0, 4611), (2570, 4499)]]
