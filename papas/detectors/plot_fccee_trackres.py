import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import csv
import copy

data = []
titles = []
with open('fccee_trackres_2.csv') as csvfile:
    reader = csv.reader(csvfile)
    first = True
    for row in reader:
        if first:
            titles = row
            first = False
            continue
        for i, dummy in enumerate(row):
            row[i] = row[i].replace(',', '.')
        print '\t'.join(row)
        data.append(row)

ndata = np.array(data, dtype=np.float)

def func(x, a, b, c):
    return np.sqrt( a ** 2 + (b / x**c) ** 2 )

xspace = np.logspace(0, 3)

for icol in range(1, len(titles)):
    print icol
    title = titles[icol]
    x = ndata[:, 0]
    y = ndata[:, icol]
    plt.loglog(x, y, "o")
    popt, pcov = curve_fit(func, x, y)
    def fitted_func(x):
        return func(x, *popt)
    plt.plot(xspace, fitted_func(xspace))    
    print popt
    
plt.show()

##x = np.logspace(0, 3)
##
##dx = sig_ptovpt2[:, 0]
##dy = sig_ptovpt2[:, 1]
##plt.loglog(dx, dy, "o")
##plt.gca().set_xlim([1, 500.])
##plt.gca().set_ylim([1e-6,1e-1])
##
##def func(x, a, b):
##    return np.sqrt( a ** 2 + (b / x) ** 2)
##
##popt, pcov = curve_fit(func, dx, dy)
##
##def fitted_func(x):
##    return func(x, *popt)
##
##plt.plot(x, fitted_func(x))
##
##plt.show()
