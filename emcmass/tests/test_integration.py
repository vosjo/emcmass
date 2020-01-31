
import pytest

import numpy as np

from emcmass import mcmc, models


def test_integration_BDm11162():
    """
    Test of observed system BD-11.162:
      Teff = 5700 +- 50
      L = 1.38 +- 0.50
      R = 1.18 +- 0.10
      log_g = 4.7 +- 0.2
      M_H = -0.40 +- 0.08

    Expected parameters:
    [Fe/H] = -0.24
    M = 0.82 Msol
    EEP = 275
    """
    models.parameters = ['mass_init', 'M_H_init', 'phase']

    variables = ['log_R', 'M_H', 'log_g', 'log_L', 'log_Teff']
    limits = [[0.1, 2.0], [-1.5, 0.5], [100, 1000]]
    y = np.array([0.07188201, -0.4,         4.7,         0.13987909,  3.75587486])
    yerr = np.array([0.03680424, 0.08,       0.2,        0.15735145, 0.00380956])
    model = 'mist'

    mcmc_kws = dict(nwalkers=100,
                    nsteps=1000,
                    nrelax=100,
                    a=10)

    results, samples = mcmc.MCMC(variables, limits, y, yerr, return_chain=True,
                                model=model, **mcmc_kws)

    M_H = -0.24
    M_init = 0.82
    EEP = 275

    assert np.abs(results['M_H_init'] - M_H) / M_H < 0.03, "Error on initial metallicity is larger than 3%"
    assert np.abs(results['mass_init'] - M_init) / M_init < 0.03, "Error on initial mass is larger than 3%"
    assert np.abs(results['phase'] - EEP) / EEP < 0.03, "Error on EEP is larger than 3%"
