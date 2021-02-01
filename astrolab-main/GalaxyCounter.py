from astropy.io import fits
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma
from astropy.nddata import Cutout2D
from astropy.nddata import CCDData
from astropy.visualization import ZScaleInterval

starcoords = [[(2161,3812),(2103,3710)], #coordinates for masking the original image by eye to remove
              [(2445,3441),(2484,3384)], #blooming items and extremely bright stars: anything spurious
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
    applies function to all coordinates in rectangle
    :param function: any function
    :param uppercorner: corner on top [larger y], expect an (x,y) format (x,y, indices)
    :param lowercorner: oorner on bottom [smaller y], expect an (x,y) format (x,y indices)
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
    :param arr: 2D array of the data [pixel counts] of the fits image
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
        print(np.amax(datacopy))
        #print(np.amax(datacopy))
        
    return source_coords, brightness_vals

def findradiusandmask(array, coordinate, cutoff=0):
    """
    finds radius of galaxy and masks
    :param array: 2D array of data
    :param coordinate: tuple of form (x,y) x,y indices of array
    :param cutoff: value at which you decide a pixel is background noise
    :return: returns an array containing the pixel values within the galaxy, and the coordinates making
            up the circle of the galaxy
    """
    x = coordinate[0]
    y = coordinate[1]
    mask = ma.getmask(array)
    print(mask)
    arraydata = ma.getdata(array)
    values = []
    where = []
    bg_vals = []
    flux = 0  # initialise a flux value
    i = 1  # initialise i for the loop
    if array[y][x] > 5000:
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
    print(radius)
    is0 = False # initialise is0 trigger: ignore galaxy if there is a zero value in it, it is a galaxy at the border of the image
    if radius > 2:  # Ensuring we only count the galaxy if it has a radius larger than 2, as a lower radius likely indicates noise.

        raditer = rad_bg  # initialise a radius value to iterate over
        while raditer >= (-1) * rad_bg:  # circle finding, loop over x and y coords

            xi = raditer  # initialise xi as distance along axis relative to x
            yi = int(np.sqrt(rad_bg ** 2 - raditer ** 2))  # initialise yi as maximum "height" within circle

            while rad_bg ** 2 >= xi ** 2 + yi ** 2:  # scan downwards along y axis at x = x+xi, mask at each point

                if array.shape[0] > y + yi and array.shape[1] > x + xi and radius ** 2 >= xi ** 2 + yi ** 2:
                    if arraydata[y+yi][x+xi] == 0:
                        is0 = True
                    values.append(array[y + yi][x + xi])
                    where.append((x + xi, y + yi))
                    array = mask_value(array, (y + yi, x + xi))
                    flux += arraydata[y + yi][x + xi]  # sums even if there's an overlap with another galaxy (for ease
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

    elif radius <= 2:  # mask out all galaxies with a radius smaller than or equal to 2

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


def var_aperture(array, source_lim, rad_lim, centered=False):
    """
    find brightest pixel values down to n, for each pixel value finds a "circular" region of light
    and masks the entire region which i will call a galaxy
    :param array: 2d array to be analysed
    :param n: cutoff value below which a pixel is not counted as a source
    :param m: cutoff value below which a pixel is counted as background
    :param centered: return the center coordinates of the galaxy

    :return: max_vals: 2d array containing pixel values of each galaxy
             where: 2d array containing tuples containing coordinates in (x,y) indices of each pixel in each galaxy
             fluxes: 1d array containing summed flux values of each galaxy
    """
    i = True
    max_vals = []
    fluxes = []
    centers = []  # measure the center of each galaxy
    where = []  # coordinates of pixels in each galaxy
    while i:
        maxval = np.amax(array)
        print(maxval)
        if maxval <= source_lim:
            break

        else:
            where1 = np.argmax(array)  # returns index in flattened arraycopy for first occurrence of maxval
            where2 = np.unravel_index(where1, array.shape)  # back to a 2d coord
            print(where2)

            values, where3, lightsum, bg_values, array = findradiusandmask(array, (where2[1], where2[0]), rad_lim)

            if values == None:
                continue

            else:
                bg_av = np.median(bg_values)
                values = [e - bg_av for e in values]
                print(lightsum - len(values) * bg_av)
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
