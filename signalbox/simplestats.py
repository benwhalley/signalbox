from __future__ import division
from math import *

def median_low(x):
    return sorted(x)[int(ceil(len(x)/2))-1]

def mean(x):
    return float((sum(x)/len(x)))

def stdev(x):
    try:
        std = []
        for value in x:
            std.append(pow((value - (sum(x)/len(x))), 2))
        stddev = sqrt(sum(std)/len(std))
        return float(stddev)
    except:
        return None