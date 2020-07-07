# EMCMASS

Determine stellar masses by fitting MIST stellar evolution models to observed 
atmospheric parameters. Uses the Markov chain Monte Carlo  implemented in EMCEE.

[![Documentation Status](https://readthedocs.org/projects/emcmass/badge/?version=latest)](https://emcmass.readthedocs.io/en/latest/?badge=latest)

## Instalation

The simplest way to install EMCMASS is using pip from the terminal. This will install EMCMASS in the local folder.

    pip install git+https://github.com/vosjo/emcmass.git#egg=emcmass

To uninstall EMCMASS, run:

    pip uninstall emcmass
    
## Command line usage

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

More options can be seen with the help command:

    emcmass -h

## working with input files

Writing all parameters on the command line can be cumbersome. Therefore EMCASS provides an option to use an input file 
containing all parameters and the requested setup. This file has to follow the 'yaml' format. A default file can be 
created with the '-empty' option:

    emcmass -empty test_star

will create an yaml file with the default setup named 'test_star.yaml'

The format of such an input file is the following:

```yaml
# parameters of the evolution models to fit
parameters: [mass_init, M_H_init, phase]
# limits that you want to apply to the parameters (same order as parameters)
limits:
- [0.1, 2.0]
- [-1.5, 0.5]
- [100, 400]
# Observables name: [value, error]
observables: 
  Teff: [5740, 50]
  L: [1.0, 0.1]
  R: [1.0, 0.1]
  log_g: [4.5, 0.5]
  M_H: [0.0, 0.1]
# The name of the evolution model to use (only mist is supported for now)
model: mist
# setup for the MCMC algorithm
nwalkers: 100    # total number of walkers
nsteps: 2000     # steps taken by each walker (not including burn-in)
nrelax: 500      # burn-in steps taken by each walker
a: 10            # relative size of the steps taken
# set the percentiles for the error determination 
percentiles: [16, 50, 84] # 16 - 84 corresponds to 1 sigma
# output options
datafile: none   # filepath to write results of all walkers
plot1:
 type: fit
 path: test_star_fit.png
plot2:
 type: distribution
 path: test_star_distribution.png
 parameters: ['mass_init', 'phase', 'M_H_init']
plot3:
 type: HR
 path: test_star_HR.png
```

This file can be used as input for emcmass with the '-f' option

    emcmass -f test_star.yaml
    
## output

The main output of EMCMASS is of course the best fitting mass and its error. But EMCMASS can produce several figures 
that can help with the interpretation of the results. When using the command line option, you can add the '--plot' 
flag to get the three possible figures. When using the input file option, you can specify which figures you want 
in the plot part of the input file. The three possible figures are:

1) The 'fit' image:

![example fit image](https://raw.githubusercontent.com/vosjo/emcmass/master/docs/source/images/example_fit.png)

2) The distribution of the parameters

![example distribution image](https://raw.githubusercontent.com/vosjo/emcmass/master/docs/source/images/example_distribution.png)

3) The observations with the best fitting model in the HR diagram

![example HR image](https://raw.githubusercontent.com/vosjo/emcmass/master/docs/source/images/example_HR.png)
