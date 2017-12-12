import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

sig_ptovpt2 = np.array(
    [[1, 3e-3],
    [5, 4e-4],
    [10, 2.e-4],
    [100, 5e-5],
    [500, 3e-5]]
)

x = np.logspace(0, 3)
dx = sig_ptovpt2[:, 0]
dy = sig_ptovpt2[:, 1]
plt.loglog(dx, dy, "o")
plt.gca().set_xlim([1, 500.])
plt.gca().set_ylim([1e-6,1e-1])

def func(x, a, b):
    return np.sqrt( a ** 2 + (b / x) ** 2)

popt, pcov = curve_fit(func, dx, dy)

def fitted_func(x):
    return func(x, *popt)

plt.plot(x, fitted_func(x))

plt.show()
