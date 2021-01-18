import scipy as sp
import random as rand

def addsource (array, x, y):
    """
    replaces values at coordinates (x,y) in array with random values
    :param array: array to be added to
    :param x: coordinate x value
    :param y: coordinate y value
    :return: returns array with added values
    """
    source = rand.randint(3, 10)
    array[y - 1][x - 1] = source
    return array


def addsources (array, x):
    """
    replaces values at multiple coordinates in array with random values
    :param array: array to be added to
    :param x: set of coordinates ( tuples or arrays)
    :return: returns array with added values
    """

    for i in x:
        addsource(array, i[0], i[1])

    return array


def findsources (array, minimum):
    """
    finds values in array with value larger than or equal to the minimum value
    and counts how many of each value is the array
    :param array: array to be counted
    :param minimum: minimum value to be counted
    :return: dictionary with values as keys as frequency as dictionary values
    """
    arraycopy = array.copy()
    arraycopy1d = arraycopy.flatten()
    dict = {}
    for i in range(len(arraycopy1d)):
        if arraycopy1d[i] >= minimum:
            if arraycopy1d[i] in dict:
                dict[arraycopy1d[i]] += 1
                i += 1
            else:
                dict[arraycopy1d[i]] = 1
                i += 1
        else: i += 1
    return dict

def findbrightestnum (data, n):
    """
    Args:
        data:: array
        n:: int
            Number of iterations.
    Returns
        max_array::array
            Largest to smallest pixel values found.
        where:: array
            The corresponding coordinates for these values.
    """
    datacopy = data.copy()
    max_array = []
    where = []
    
    for i in range(n):
        maxval = sp.amax(datacopy)
        where1 = sp.argmax(datacopy) #returns index in flattened arraycopy for first occurrence of maxval
        where2 = sp.unravel_index(where1, datacopy.shape) #back to a 2d coord
        datacopy[where2[0]][where2[1]] = 0 # Marking the brightest value that has been found with a 0 
        where.append(where2)
        max_array.append(maxval)
        i += 1
        
    return max_array , where

def findbrightestmin (data, min_lim):
    """
    Finds the largest pixel values and their coordinates up until a specified limit.
    Args:
        data:: array
        min_lim:: int
            Pixel value limit we want to stop counting at.
    Returns:
        max_array:: array
            Array of maximum pixel values found
        where:: array
            The corresponding coordinates of these values.
    """
    datacopy = data.copy()
    max_array = []
    where = []
    while True:
        maxval = sp.amax(datacopy)
        if maxval <= min_lim:
            break
        else:
            where1 = sp.argmax(datacopy) #returns index in flattened arraycopy for first occurrence of maxval
            where2 = sp.unravel_index(where1, datacopy.shape) #back to a 2d coord
            datacopy[where2[0]][where2[1]] = 0
            where.append(where2)
            max_array.append(maxval)
            
    return max_array, where

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

def replace(array, coords):
    array[coords[0]][coords[1]] = 20
    return array


background = sp.zeros((10,10), dtype = int)

coords = ((1,1),(2,2) , (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,9), (10,10))
sky =  addsources(background,coords)

print(sky)

huh, who =  findbrightestnum(sky, 4)
huh2, who2 = findbrightestmin(sky, 4)



print(huh, who, huh2, who2 )
