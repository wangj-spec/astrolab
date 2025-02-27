"""
Created on Tue Jan 26 15:30:27 2021

@author: leonardobossi1
"""

from astropy.io import fits
import numpy as np
import numpy.ma as ma
from astropy.nddata import CCDData

#coordinates for masking the original image by eye to remove
#blooming items, bright stars, as well as areas with high noise (edges of image)

starcoords = [[(2161,3812),(2103,3710)], 
              [(2445,3441),(2484,3384)], 
              [(2079,1452),(2097,1405)],
              [(2064,1449),(2113,1382)],
              [(2105,2335),(2158,2284)],
              [(2153,3348),(2313,3231)],
              [(1369,3283),(1513,3141)],
              [(1380,3165),(1462,2955)],
              [(1421,2967),(1454,0)],
              [(1176,446),(1607,425)],
              [(1463,488),(1399,144)],
              [(1077,340),(1716,306)],
              [(2427,417),(2569,0)],
              [(2569,4610),(2479,417)],
              [(721, 3417),(832,3194)],
              [(852, 2361),(952,2206)],
              [(925, 2833),(1026,2694)],
              [(530, 4128),(597,4061)], [(1462,225),(1471,217)], [(1640,355),(1646, 340)],
              [(1425, 4020),(1492,3997)], [(1466,343), (1463, 340) ], [(1389,241),(1477,229)],
              [(1415, 4506), (1474, 3450)], [(1080,315),(1017,314)], [(1103,427),(1179,425)],
              [(0, 4610), (137,0)],[(2438,3446), (2518, 3354)],[(1024,453),(1044,423)],
              [(0,140), (2569, 0)],[(1389, 1810),(1443, 1753)], [(1677,448), (1597,416)],
              [(1380, 3555),(1470, 3308)], [(1210, 3380), (1657, 3008)], [(1297, 151), (1551, 94)],
              [(2099, 4610), (2569, 4388)], [(0, 4610), (2569, 4499)]]


def openfits(filename):
    """
    opens a .fits file and returns the data and header respectively
    :param filename: .fits filename as a string
    :return: data: 2D array of data
             header: header of the .fits file
    """
    hdulist = fits.open(filename)
    data = hdulist[0].data
    header = hdulist[0].header
    
    return data, header

def openccd(filename):
    """
    opens the data of .fits file with a mask as a masked array
    :param filename: .fit filename as a string
    :return: 2D masked array of data
    """
    ccd = CCDData.read(filename)
    maskedarray = np.asanyarray(ccd)
    
    return maskedarray

def rectanglecoord (array, function, uppercorner, lowercorner):
    """
    applies input function to all coordinates in rectangle
    Args:
      function: any function
      uppercorner: list
        corner on top [larger y], expect an (x,y) format (x,y, indices)
      lowercorner: list
        corner on bottom [smaller y], expect an (x,y) format (x,y indices)
    :return: array with function applied to relevant portions
    """
    xu = uppercorner[0]
    xd = lowercorner[0]
    yu = uppercorner[1]
    yd = lowercorner[1]
    if xu <= xd:
        for j in range(yu - yd + 1):
            for i in range(xd - xu + 1):
                array = function(array, [ yu - j , xu + i ])

    elif xu > xd:
        for j in range(yu - yd + 1):
            for i in range(xu - xd + 1):
                array = function(array, [ yu - j , xd + i ])

    return array


def mask_value(arr, coords):
    '''
    Function masks one value in a 2d array given its cooredinates
    Args:
        arr:: 2d masked array
        coords: list
            coordinates of value that are to be masked
            
    Returns:
        arr:: ma array
            masked array with value masked
    '''
    arr = ma.array(arr)
    arr[coords[0], coords[1]] = ma.masked
    
    return arr

def maskstars(arr):
    """
    masks stars according to the star coordinates in this file.
    Args:     
     arr: 2D array of the data [pixel counts] of the fits image
    :return: maskedarray: 2D masked array of the image
    """
    for coord in starcoords:
        arr = rectanglecoord(arr, mask_value, coord[0], coord[1])
    ccd = CCDData(arr, unit="adu")
    ccd.write("starsmasked.fits", overwrite=True)
    return arr


def fixed_aperture(data, bg_lim, mask_size):
    '''
    Counts galaxies using a fixed aperature
    Args:
        data:: array
        bg_lim:: int
            brightness limit for when function stops counting object as a galaxy
        mask_size:: int
            Length of the fixed aperature mask in pixel values (square mask)
    Returns:
        source_coords: list
            Coordinates of the galaxies
        brightness_vals: list
            list of the brightest pixel in each source.
        tot_galaxies:: int
            Number of galaxies counted
        datacopy::array
            Masked image
    '''
    datacopy = data.copy()
    source_coords = []
    brightness_vals = []
    
    while np.amax(datacopy) > bg_lim:
        
        brightness_vals.append(np.amax(datacopy))
        coords1 = np.argmax(datacopy)
        coords2 = np.unravel_index(coords1, datacopy.shape) #2d coordinate of the brightest pixel
        
        source_coords.append(coords2)
        upp_corner = [coords2[1]+mask_size, coords2[0] + mask_size] # coords2[1] used first as the first index corresponds to the x value
        low_corner = [coords2[1]-mask_size, coords2[0] - mask_size]
        datacopy = rectanglecoord(datacopy, mask_value, upp_corner, low_corner)
        
    tot_galaxies = len(brightness_vals)
    
    return source_coords, brightness_vals, tot_galaxies, datacopy

def findradiusandmask(array, coordinate, minsize, cutoff=0):
    """
    finds radius of galaxy and masks
    Args:
      array: np.array
        2D array of the data
      coordinate: tuple
        tuple of form (x,y) x,y indices of array
      cutoff: float
        value at which you decide a pixel is background noise
      minsize: int
        minimum size of galaxy counted ( radii lower than these are not counted as galaxies).
    Returns:
      values:: np.array
        Individual pixel values of the galaxy 
      where:: np.array
        Coordinates of the pixels within the galaxy
      flux:: float
        Total summed pixel count of the total light emitted from the galaxy
      bg_vals:: np.array
        Array of background values for that galaxy
      array:: ma.array
        Input array with detected galaxy masked.
    """
    x = coordinate[0]
    y = coordinate[1]
    mask = ma.getmaskarray(array)
    arraydata = ma.getdata(array)
    values = []
    where = []
    bg_vals = []
    flux = 0  # initialise a flux value
    i = 1  # initialise i for the loop
    if array[y][x] > 5000:  # failsafe cutoff size for galaxies: no galaxy is likely to be this large,
                            # especially if the brightest value is not so bright, so any galaxy found to be too large
                            # is deemed an error and a fixed aperture method is used
        radlim = 50
    else:
        radlim = 30

    while True:  # radius finding
        if array.shape[0] > y + i:
            if array[y + i][x] > cutoff:
                if i <= radlim:
                   i += 1  # keep going outwards if value greater than cutoff value
                else:
                    radius = 7
                    rad_bg = 9
                    break
            else:
                radius = i - 1  # stop at threshold and record radius of values
                rad_bg = i + 1

                break

        else:  # if scanning up gets out of bounds, scan downwards (for galaxies on edge of images)
            if array[y - i][x] > cutoff:
                i += 1  # keep going outwards if value greater than cutoff value
            else:
                radius = i - 1  # stop at threshold and record radius of values
                rad_bg = i + 1

                break
            
    is0 = False # initialise is0 trigger: ignore galaxy if there is a zero value in it, it is a galaxy at the border of the image
    if radius > minsize:  # Ensuring we only count the galaxy if it has a radius larger than minsize, as a lower radius likely indicates noise.

        raditer = rad_bg  # initialise a radius value to iterate over
        while raditer >= (-1) * rad_bg:  # circle finding, loop over x and y coords

            xi = raditer  # initialise xi as distance along axis relative to x
            yi = int(np.sqrt(rad_bg ** 2 - raditer ** 2))  # initialise yi as maximum "height" within circle

            while rad_bg ** 2 >= xi ** 2 + yi ** 2:  # scan downwards along y axis at x = x+xi, mask at each point

                if array.shape[0] > y + yi and array.shape[1] > x + xi and radius ** 2 >= xi ** 2 + yi ** 2 and mask[y+yi][x+xi] == False:
                    if arraydata[y+yi][x+xi] == 0:
                        is0 = True
                    values.append(array[y + yi][x + xi])
                    where.append((x + xi, y + yi))
                    array = mask_value(array, (y + yi, x + xi))
                    flux += arraydata[y + yi][x + xi]  
                    yi -= 1

                elif radius ** 2 < xi ** 2 + yi ** 2 and array.shape[0] > y + yi and array.shape[1] > x + xi and mask[y+yi][x+xi] == False:

                    bg_vals.append(arraydata[y + yi][x + xi])

                    # array = mask_value(array, (y+yi,x+xi))
                    yi -= 1

                else:  # If out of bounds, keep scanning downwards
                    yi -= 1

            raditer -= 1
            
        if is0:
            return None, None, None, None, array
        else:
            return values, where, flux, bg_vals, array

    elif radius <= minsize:  # mask out all galaxies with a radius smaller than or equal to minsize

        raditer = radius  # initialise a radius value to iterate over

        while raditer >= radius * (-1):  # circle finding, loop over x and y coords

            xi = raditer  # initialise xi as distance along axis relative to x
            yi = int(np.sqrt(radius ** 2 - raditer ** 2))  # initialise yi as maximum "height" within circle

            while radius ** 2 >= xi ** 2 + yi ** 2:  # scan downwards along y axis at x = x+xi, mask at each point

                if array.shape[0] > y + yi and array.shape[1] > x + xi:
                    array = mask_value(array, (y + yi, x + xi))
                    yi -= 1
                else:
                    yi -= 1

            raditer -= 1

        return None, None, None, None, array


def var_aperture(array, source_lim, rad_lim, centered=False, minsize=2):
    """
    find brightest pixel values down to n, for each pixel value finds a "circular" region of light
    and masks the entire region which i will call a galaxy
    Args:
      array: ma.array
        2d  masked array to be analysed
      source_lim:: float
        cutoff value below which a pixel is not counted as a source
      rad_lim:: float
        cutoff value below which a pixel is counted as background
      centered: Bool
        If true, function also return the center coordinates of the galaxy, default to False
      minsize: int
        define the minimum radius size of galaxies being counted, default to 2 pixels.
    Returns:
      max_vals: np.array
        2d array containing pixel values of each galaxy
      where: np.array
        2d array containing tuples containing coordinates in (x,y) indices of each pixel in each galaxy
      fluxes: np.array
        1d array containing summed flux values of each galaxy
      array:: ma.array
        Original array after masking 
    """
    i = True
    max_vals = []
    fluxes = []
    centers = []  # measure the center of each galaxy
    where = []  # coordinates of pixels in each galaxy
    while i:
        maxval = np.amax(array)
        if maxval <= source_lim:
            break

        else:
            where1 = np.argmax(array)  # returns index in flattened arraycopy for first occurrence of maxval
            where2 = np.unravel_index(where1, array.shape)  # back to a 2d coord
            print('Galaxy found at ' +str(where2))

            values, where3, lightsum, bg_values, array = findradiusandmask(array, (where2[1], where2[0]), minsize, rad_lim)

            if values == None:
                continue

            bg_av = np.median(bg_values)
            values = [e - bg_av for e in values]
            if lightsum - len(values) * bg_av < 0: #if the overall flux counted comes out to be
                                                  # negative, this is a clearly unphysical result
                                                    # which is due to the flaws in our method
                continue
            else:
                fluxes.append(lightsum - len(values) * bg_av)
                centers.append(where2)
                where.append(where3)
                max_vals.append(values)

    fluxes.sort() #preparing the flux data for analysis
    if centered == False:
        return max_vals, where, fluxes, array

    else:
        return max_vals, where, fluxes, centers, array

def tally(array):
    """
    finds values in array and counts how many of each value is the array
    :param array: array to be counted (1 dimensional)
    :return: dictionary with values as keys as frequency as dictionary values
    """

    dict = {}
    for i in range(len(array)):

        if array[i] in dict:
            dict[array[i]] += 1
            i += 1
        else:
            dict[array[i]] = 1
            i += 1

    return dict


def find_index(m_low, m_high, m_array):
    '''
    Args:
        m_low::float
        m_high::float
            The lower and higher limits of the magnitude bin.
        m_array::array
            Array of data scanning through.
    Returns:
        j::float
        h::float
            The corresponding indices the edges of the bins refers to.
    '''
    j = 0
    h = len(m_array) - 1
    
    if m_low <= m_array[len(m_array)-1]:
        j = len(m_array)-1
    else:
        while m_array[j] >= m_low: 
            j += 1
    
    if m_high >= m_array[0]:
        h = 0 
    else:
        while  m_array[h] <= m_high:
            h -= 1

    return j, h


