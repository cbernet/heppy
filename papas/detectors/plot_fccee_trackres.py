import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import csv
import copy
import pprint
import math

data = []
titles = []
with open('fccee_trackres.csv') as csvfile:
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

def sigpt_over_pt2(x, a, b, c):
    return np.sqrt( a ** 2 + (b / x**c) ** 2 )

xspace = np.logspace(0, 3)

results = list()
fig1 = plt.figure()
plt1 = fig1.add_subplot(111)
fig2 = plt.figure()
plt2 = fig2.add_subplot(111)

for icol in range(1, len(titles)):
    title = titles[icol]
    x = ndata[:, 0]
    y = ndata[:, icol]
    plt1.loglog(x, y, "o")
    popt, pcov = curve_fit(sigpt_over_pt2, x, y)
    def fitted_func(x):
        return sigpt_over_pt2(x, *popt)
    plt1.loglog(xspace, fitted_func(xspace))
    plt2.loglog(xspace, fitted_func(xspace) * xspace)
    angle = 90. - float(title)
    results.append( (angle, list(popt)) )
pprint.pprint(results)
plt.show()


##x = np.logspace(0, 
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
