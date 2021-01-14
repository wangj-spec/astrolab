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


def addsources (array, minimum):
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



background = sp.zeros((10,10), dtype = int)

coords = ((1,1),(2,2) , (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,9), (10,10))
sky =  addsources(background,coords)

print(sky)

sources = findsources(background, 0)
sources2 = findsources(sky, 2)

print(sources, sources2)