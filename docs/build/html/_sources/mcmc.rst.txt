 
MCMC setup
==========

The Markov chain Monte Carlo algorithm implemented in the :py:mod:`emcee` package is used. This reduces the effort of implementing MCMC to defining the prior and likelihood functions, and providing some basic setup parameters for emcee.

The **Seriously Kick-Ass MCMC** :py:mod:`emcee` package is a pure python implementation of the Goodman & Weare’s Affine Invariant Markov chain Monte Carlo (MCMC) Ensemble sampler. The emcee package can be obtained `here <http://dan.iel.fm/emcee/current/>`_, and it is described in `Foreman-Mackey et al. 2012 <https://arxiv.org/abs/1202.3665>`_.

Parameters & Observables
------------------------

The model parameters (:math:`\theta`) that are used to predict the observations ( *y* and *yerr* ) are initial mass, initial metalicity and age (:math:`M_i, [M/H]_i, \tau`). These parameters are defined as follows:

   ==================  =========  =========================
   Parameter           Name       Unit
   ==================  =========  =========================
   initial mass        Mass_init  :math:`M_{\odot}`
   initial metalicity  M_H_init   dex
   age                 log_Age    :math:`\log{ \tau / yr }`
   ==================  =========  =========================

The observable parameters are effective temperature, luminosity, surface gravity, radius and metalicity. The observed metalicity can be different from the initial metalicity due to diffusion and mixing processes during the lifetime of the star. All evolution models shipped with emcmass use the same names and units for the observables, they are defined as follows:

   =====================  ==========  ===========================
   Observable             Name        Unit
   =====================  ==========  ===========================
   effective temperature  log_Teff    :math:`\log{T_{eff} / K}`
   luminosity             log_L       :math:`\log{L / L_{\odot}}`
   surface gravity        log_g       :math:`\log{g}` in cgs
   radius                 log_R       :math:`\log{R / R_{\odot}}`
   metalicity             M_H         [M/H]
   =====================  ==========  ===========================
   
Priors
------

emcmass uses a flat prior for all model parameters (:math:`\theta`). The log-prior function is defined as returning *0* if all parameters are within their limits and returning :math:`-\inf` if any parameter is outside its limit. 

This prior is defined in the :py:func:`emcmass.emcmass.lnprior` function. It takes as arguments the model parameters (:math:`\theta`), and the limits on the parameters as a list of tuples. In the following example the masses are limited between 0.1 and 2.0 Msol, metalicity between -1 and 0.25 and age between 1 Myr and 1 Gyr:

>>> limits = [(0.1, 2.0), (-1, 0.25), (6.0, 9.0)]
>>> lnprior([0.91, -0.125, 6.67], limits)
    0
>>> lnprior([2.31, -0.125, 6.67], limits)
    -inf
    
Likelihood function
-------------------

The likelihood of observing observables *y* for a given model :math:`\theta` is defined as :math:`L(y|\theta) = \exp{(-\chi^2/2)}`, where the chi squared function is calculated as:

.. math::
   \chi^2 = \sum_i \frac{(y_i - m(\theta)_i)^2}{yerr_i^2}
   
where :math:`m(\theta)` are the theoretical values for the given model parameters :math:`\theta`.

The likelihood function is defined in the :py:func:`emcmass.emcmass.lnlike` function. Its arguments are the model parameters :math:`\theta`, the observables *y* and the errors on the observables *yerr*. It will call the :py:func:`emcmass.models.interpolate` function to determine the theoretical values for the observables. 

Markov chain
------------

To create the Markov chains with the probability distribution :math:`p(\theta|y)`, a *Metropolis-Hastings* jump probability distribution is used. This is also the standard setup in emcee. It is defined as follows. A trial point :math:`\theta' = \theta + \delta \theta` in the vicinity of the current model parameters is picked. If any of the model parameters :math:`\theta'` are outside the valid range, the point is imediatly rejected. This is achieved by the prior function returning :math:`-\inf` if the model parameters are outside their limits. Otherwise, the probability of accepting the new point is given as:

.. math::
   :nowrap:
   
   \begin{eqnarray}
   p = & 1 & {\rm if\ \ } L(\theta'|y) > L(\theta|y) \\
       & L(\theta'|y) / L(\theta|y) & {\rm if\ \ } L(\theta'|y) \le L(\theta|y)
   \end{eqnarray}

Meaning that if the likelihood of the new model is higher then the current one it is always accepted, but if it is lower the probability of accepting it depends on the fraction of the likelihoods.