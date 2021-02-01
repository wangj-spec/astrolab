import GalaxyCounter as gal
import numpy as np
import matplotlib.pyplot as plt
from astropy.nddata import CCDData

sourcelim = 3500    # don't count anything with a max pixel count under 3500 as a galaxy
radiuslim = 3443    # don't count pixels with a pixel count under 3443 as part of a galaxy

unuseddata, header = gal.openfits("mosaic.fits")
maskeddata = gal.maskstars(unuseddata)# only use this line if first time running
data = gal.openccd("starsmasked.fits")

galaxyvals, galaxylocales, galaxyfluxes, data = gal.var_aperture(data, sourcelim, radiuslim)

magnitudes = header["magzpt"] + (-1*2.5)*sp.log10(galaxyfluxes) # according to definition
fluxfreq = gal.tally(magnitudes)    #finds the frequency of each galaxy magnitude in the image
total = sum(fluxfreq.values())

nm = []
mpix = []
for i in fluxfreq:
    total -= fluxfreq[i]
    nm.append(total)
    mpix.append(i)

nm = np.log10(nm)

plt.scatter(mpix[:-1], nm[:-1], label='Data points plotted using variable aperature galaxy counter')
z = sp.polyfit(mpix[30:-30], nm[30:-30], 1)     #indices of slice prone to change depending on the data

mpix_y = [e * z[0] for e in mpix]

plt.plot(mpix[30:-30], mpix_y[30:-30] + z[1], color='k', \
         label='Linear plot with gradient = ' + str(round(z[0], 2)))

plt.xlabel('Magnitude')
plt.ylabel('$Log_{​​​​​​​10}​​​​​​​$N(m)')
plt.legend()
plt.grid()
plt.show()

