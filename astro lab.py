from astropy.io import fits
import scipy as sp
import matplotlib.pyplot as plt

hdulist = fits.open("mosaic.fits")
hdulist.info()
data = hdulist[0].data
print(data)


data1d = data.flatten()
print(data1d)

data1dmod = data1d[data1d > 4000]
plt.hist(data1dmod, bins = 1000)
plt.show()

hdulist.close()


starcoords2 = [[(721, 3417), (832, 3194)], [(852, 2361), (952, 2206)], \
               [(925, 2833),(1026, 2694)], [(530, 4128), (597, 4061)], \
                [(1425, 4006) ,(1492, 3997)] , [(1416, 4506),(1474, 3450)],\
                [(0, 4611), (137, 0)], [(0,0), (2569, 140)], \
                        [(2099, 4611), (2570, 4388)], [(0, 4611), (2570, 4499)]]
