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


