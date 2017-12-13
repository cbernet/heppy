import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

pars = {
    'barrel':[1.036, 4.452, -2.458],
    'endcap':[1.071, 9.471, -2.823]
}

def response(x, *pars):
    return pars[0] / (1 + np.exp((x-pars[1]) / pars[2]))

x = np.linspace(0, 100)
plt.plot(x, response(x, *(pars['barrel'])))
plt.plot(x, response(x, *(pars['endcap'])))
plt.show()

