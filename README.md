# EMCMASS

Determine stellar masses by fitting MIST stellar evolution models to observed 
atmospheric parameters. Uses the Markov chain Monte Carlo  implemented in EMCEE.

[![Documentation Status](https://readthedocs.org/projects/emcmass/badge/?version=latest)](https://emcmass.readthedocs.io/en/latest/?badge=latest)

## Instalation

The simplest way to install EMCMASS is using pip from the terminal. This will install EMCMASS in the local folder.

    pip install git+https://github.com/vosjo/emcmass.git#egg=emcmass

To uninstall EMCMASS, run:

    pip uninstall emcmass
    
## Mass determination

EMCMASS will fit theoretical evolution models to observed atmospheric parameters as effective temperature, surface 
gravity, radius, luminosity and metallicity. The best fitting model will determine the mass and potentially the age of 
the observed star.

EMCMASS can be used directly from the command line. The most basic use only supplies the observables with their errors
and uses the default settings of the MCMC algorithm. In the case below we use emcmass to determine the mass of a star 
with Teff = 4677 +- 500 K, logg = 4.70 +- 0.40 and a metallicity of [Fe/H] = -0.42 +- 0.25

    emcmass log_Teff 3.67 0.05 log_g 4.70 0.40 M_H -0.42 0.25
    
The output of this process will look like this:

```
================================================================================
                                   EMCMASS
================================================================================

Stellar evolution models:  mist 

Limits applied to the model grid parameters:
   mass_init = 0.1 -> 5.0
   M_H_init = -1.5 -> 0.5
   phase = 0 -> 400

Observables included in fit:
   log_Teff = 3.67 +- 0.05
   log_g = 4.7 +- 0.4
   M_H = -0.42 +- 0.25

MCMC setup:
   # walkers: 100
   # steps: 1000
   # a: 2
================================================================================
New limits to match up with grid points:
[(0.1, 5.0), (-1.5, 0.5), (0.0, 400.0)]
100%|████████████████████████████████████████████████████████████| 1100/1100 [00:14<00:00, 73.50it/s]
================================================================================

Resulting parameters values and errors:
   Par          Best    Pc      emin     emax
   mass_init  = 0.654   0.617   -0.229   +0.191
   M_H_init   = -0.411   -0.348   -0.265   +0.251
   phase      = 105.404   175.610   -79.979   +85.166
```

The best fitting model has a mass of 0.654 +- 0.20 Msol.
