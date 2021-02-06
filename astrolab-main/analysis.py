"""
Created on Tue Jan 26 15:30:27 2021

@author: leonardobossi1
"""

import GalaxyCounter as gal
import numpy as np
import matplotlib.pyplot as plt
from astropy.stats import bootstrap
from astropy.utils import NumpyRNGContext
from astropy.nddata import CCDData
from scipy.optimize import curve_fit

sourcelim = 3500    # Galaxy identification limit
radiuslim = 3443    # Masking radius limit

# Masking unwanted areas of images and saving the file.
original_data, header = gal.openfits("mosaic.fits")
maskeddata = gal.maskstars(original_data) 
data = gal.openccd("starsmasked.fits")

data1dmod = original_data[original_data < 6000] # removing values larger than 6000  
freq, bins , p = plt.hist(data1dmod, 1000)

def Gaussian(x, const, sigma, u):
    '''
    Returns Guassian function for a given x value and Gaussian parameters.
    sigma::float 
        Standard deviation
    const::float 
        constant
    u::float 
        mean value

    '''
    return (const/(sigma * np.sqrt(2* np.pi))) * np.e ** (-0.5 * ((x - u)/sigma) ** 2)

# taking midpoint of the bins
mid_vals = np.zeros(len(bins) - 1)

for i in np.arange(len(bins) - 1):
    mid_vals[i] =  (bins[i] + bins[i+1]) / 2
   
    
opt_fit, cov = curve_fit(Gaussian, mid_vals, freq, [50000000, 20, 3418])

plt.plot(mid_vals, Gaussian(mid_vals, *opt_fit), label='Gaussian fit with sigma = ' \
         +str("{:.2f}".format(opt_fit[1]))+' and u= '+str("{:.2f}".format(opt_fit[2])))
plt.xlim(3300, 3600)
plt.xlabel('Value of pixel')
plt.ylabel('Occurance frequency')
plt.legend(loc=1)
plt.grid()


# Scanning the image with variable aperature
galaxyvals, galaxylocales, galaxyfluxes, data = gal.var_aperture(data, sourcelim, radiuslim)

# Apparent magnitude calculated using provided calibration
magnitudes = header["magzpt"] + (-1*2.5) * np.log10(galaxyfluxes) 

#%%

#finds the frequency of each galaxy magnitude in the image
fluxfreq = gal.tally(magnitudes)    
total = sum(fluxfreq.values())

# Generating the galaxy number count 
nm = [] 
mpix = []

for i in fluxfreq:
    total -= fluxfreq[i]
    nm.append(total)
    mpix.append(i)

lognm = np.log10(nm)

# Scatter plot of resulting data 
plt.figure()

# ignore last datapoint as this will be infinity (N=0 for last datapoint)
plt.scatter(mpix[:-1], lognm[:-1], label='Data points plotted using variable aperature galaxy counter')
z = np.polyfit(mpix[1000:1700], lognm[1000:1700], 1) # Linear fit for m = 14 - 16.5 region

mpix_y = [e * z[0] for e in mpix]

plt.plot(mpix[:-1], mpix_y[:-1] + z[1], color='k', \
         label='Linear plot with gradient = ' + str(round(z[0], 2)))

plt.xlabel('Magnitude')
plt.ylabel('$Log_{​​​​​​​10}​​​​​​​$N(m)')
plt.legend()
plt.grid()
plt.show()

# Binning values 
m_vals, data = [mpix[:-1], lognm[:-1]]

m_binned = []
vals_binned=[]

# binning values
for i in np.arange(10.5, 24.0, 0.5):
    upper, lower = gal.find_index(i, i+0.5, m_vals)
    m_binned.append((2*i + 0.5)/2)

    vals_binned.append(np.mean(data[lower:upper]))
    
plt.figure()
plt.scatter(m_binned, vals_binned, label='Binned data points from scanning full image', marker='x')

# Extracting the values before the gradient begins to flatten due to all the
# galaxies being counted     
z1 = np.polyfit(m_binned[0:8], vals_binned[0:8], 1)


y_vals = [e * z1[0] for e in m_binned]

plt.plot(m_binned ,  y_vals + z1[1], color='k', \
         label = 'Linear plot with gradient = '+str(round(z1[0],2)))
plt.xlabel('Magnitude')
plt.ylabel('$Log_{10}$N(m)')
plt.legend()
plt.xlim(10.5,19)
plt.ylim(1.25, 4)
plt.grid()


#%%
# Finding errors for the datapoints using bootstrapping
ccd1 = CCDData.read("starsmasked.fits")

test_flux = galaxyfluxes
test_flux.sort()
test_flux = np.array(test_flux[14:])


with NumpyRNGContext(1):
    bootresult = bootstrap(test_flux, 2000)
    
grad_result = []

# Obtaining plot for all resampled datasets.
for sample in bootresult:
    sample.sort()

# Finding the magnitudes using the counts and the flux calibration 

    mag = header["magzpt"] + (-1 * 2.5) * np.log10(sample)
    
    # Using the tally to find the total number of galaxies found and how many are
    # found for each specific magnitude 
    fluxfreq1 = gal.tally(mag)
    total1 = sum(fluxfreq1.values())
    
    # Generating the plot with all the datapoints
    sampleN = []
    sampleM = []
    
    for i in fluxfreq1:
        total1 -= fluxfreq1[i]
        sampleN.append(total1)
        sampleM.append(i)
        
    sampleN = np.log10(sampleN)
    
    
    m_binned1 = []
    vals_binned1=[]

    # binning values in the desired range from m = 12 to m = 15
    for i in np.arange(12, 15, 0.5):
        upper, lower = gal.find_index(i, i+0.5, sampleM)
        m_binned1.append((2*i + 0.5)/2)
        vals_binned1.append(np.mean(sampleN[lower:upper]))
    
    z_sample = np.polyfit(m_binned1, vals_binned1, 1)
    grad_result.append(z_sample[0])

gradient_err = np.std(grad_result)

print('Gradient from linear fit = '+str(z1[0]))
print('Uncertainty in the gradient calculation is '+str(gradient_err))


# Obtaining the errors in the y values (log10N)

# Creating a list of all the m and all the corresponding y values for the resamples
all_m = []
all_vals = []

# Iterating through all the samples in the bootstrap
for sample in bootresult:
    sample.sort()
        
            # Finding the magnitudes using the counts and the flux calibration 
        
    mag = header["magzpt"] + (-1 * 2.5) * np.log10(sample)
            
            # Using the tally to find the total number of galaxies found and how many are
            # found for each specific magnitude 
    fluxfreq1 = gal.tally(mag)
    total1 = sum(fluxfreq1.values())
            
            # Generating the plot with all the datapoints
    sampleN = []
    sampleM = []
            
    for i in fluxfreq1:
        total1 -= fluxfreq1[i]
        sampleN.append(total1)
        sampleM.append(i)
                
    sampleN = np.log10(sampleN)

    for i in np.arange(10.5, 22, 0.5):
        upper, lower = gal.find_index(i, i+0.5, sampleM)
        all_m.append((2*i + 0.5)/2)
        all_vals.append(np.mean(sampleN[lower:upper]))


m=[]
temp_arr=[]
err=[]

for m_val in np.arange(10.75, 21, 0.5):
             
    for i, j in enumerate(all_m):
        if j == m_val:
            # If the value of m is equal to 10.75, append all the corresponding
            # y values
            
            temp_arr.append(all_vals[i])
            
    m.append(m_val)
    
    err.append(np.std(temp_arr))
    
    # Resetting the binned values to empty list when iterating
    temp_arr = []


y_vals = [e * z1[0] for e in m_binned]

plt.plot(m_binned ,  y_vals + z1[1], color='k', \
         label = 'Linear plot with gradient = '+str(round(z1[0],2)))
    
plt.xlabel('Magnitude')
plt.ylabel('$Log_{10}$N(m)')
plt.legend()
plt.show()
plt.grid()


# Adding the Possion error in N(m)
N_vals = [10 ** e for e in vals_binned]

perr = 1/ (np.log(10) * np.array(N_vals) ** (1/2))

tot_err = err + perr[0:len(m)]

plt.figure()

plt.errorbar(m, vals_binned[0:len(m)], yerr = tot_err, fmt='kx', capsize=2)
plt.title('Plot with correlation error from bootstrapping added with the Poisson error')
plt.xlabel('Magnitude')
plt.ylabel('$Log_{10}$N(m)')
plt.grid()










