from astropy.io import fits
import scipy as sp
import matplotlib.pyplot as plt

hdulist = fits.open("mosaic.fits")
hdulist.info()
data = hdulist[0].data
print(data)

starcoords = [[(2144,3182),(2124,3710)],
              [(2453,3441),(1474,3384)],
              [(2079,1452),(2097,1405)],
              [(2099,1449),(2080,1402)],
              [(1447,4048),(1454,4019)],
              [(2153,3348),(2313,3231)],
              [(1369,3283),(1513,3141)],
              [(1410,3165),(1462,2966)],
              [(1421,2967),(1454,0)],
              [(1176,446),(1607,425)],
              [(1463,488),(1399,144)],
              [(1077,340),(1716,306)],
              [(2427,417),(2570,0)],
              [(2570,4611),(2479,417)],

data1d = data.flatten()
print(data1d)

data1dmod = data1d[data1d > 4000]
plt.hist(data1dmod, bins = 1000)
plt.show()

hdulist.close()


