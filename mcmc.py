
import numpy as np

import emcee

import models
 
#{ Define the probability funtions

def lnlike(theta, y, yerr, **kwargs):
   """
   log likelihood function
   
   There is no need to check for limits in the likelihood function because
   this is already done in the prior function
   
   This function uses :py:func:`models.interpolate` to obtain the synthetic
   values for the given parameters theta. The logarithm of the likelihood is
   calculated as:
   
   :math:`L( theta | y ) = \exp( - \chi^2 / 2 )`
   
   with:
   
   :math:`\chi^2 = \sum (model(theta) - y)^2 / yerr^2`
   
   :param theta: list of model parameters (normaly mass, fe/h and age)
   :type theta: list
   :param y: 1D array of observables
   :type y: array
   :param yerr: 1D array containing errors on every observable
   :type yerr: array
   
   :return: logarithm of the likelihood of the model parameters (theta) given 
            the observables (y) with errors (yerr)
   :rtype: float
   """
   
   # synthetic parameters
   y_syn = models.interpolate(*theta)
   
   # chi squared between model and observations
   chi2 = np.sum((y_syn - y)**2 / yerr**2)
   
   # log of the probability from the chi2
   return -chi2/2.


def lnprior(theta, limits, **kwargs):
   """
   Simple uniform (flat) prior on all three parameters if they 
   are within their range
   
   if all parameters are within the provided limits, the the returned 
   log probability is 0, otherwise it is -inf.
   
   :param theta: list of model parameters
   :type theta: list
   :param limits: limits on the model parameters
   :type limits: list of tuples
   
   :return: logarithm of the probability of the parameters (theta) given the 
            model limits
   :rtype: float
   """
   
   for val, lim in zip(theta, limits):
      if val < lim[0] or val > lim[1]:
         return -np.inf
   
   return 0
   
def lnprob(theta, y, yerr, limits, **kwargs):
   """
   full log probability function combining the prior and the likelihood
   
   will return -inf if any of :py:func:`lnprior` or :py:func:`lnlikelyhood` is 
   infite, otherwise it will return the sum of both functions.
   
   :param theta: list of model parameters (normaly mass, fe/h and age)
   :type theta: list
   :param y: 1D array of observables
   :type y: array
   :param yerr: 1D array containing errors on every observable
   :type yerr: array
   :param limits: limits on the model parameters
   :type limits: list of tuples
   
   :return: the sum of the log prior and log likelihood
   :rtype: float
   """
   lp = lnprior(theta, limits)
   if not np.isfinite(lp):
      return -np.inf
   
   ll = lnlike(theta, y, yerr)
   if not np.isfinite(ll):
      return -np.inf
   
   return lp + ll

#}

#{ MCMC stuff

def MCMC(variables, limits, obs, obs_err, 
         model='mist', nwalkers=100, nsteps=1000, percentiles=[16, 50, 84], 
         return_chain=False, **kwargs):
   """
   Main MCMC function
   
   :param parameters: list of model parameters to interpolate in between
   :type parameters: list
   :param variables: list of observable variables to be used in the likelihood function
   :type variables: list
   :param limits: list of limits on the model parameters. Each limit is one tuple 
                  containing (min, max)
   :type limits: list of tuples
   :param obs: array of the observed values for the variables
   :type obs: np.array
   :param obs_err: array of the errors on the observations
   :type obs_err: np.array
   :param model: name of the stellar evolution models
   :type model: str
   :param nwalkers: number of walkers to use (at least twice as many as parameters)
   :type nwalkers: int
   :param nsteps: number of steps each walker will take
   :type nsteps: int
   :param percentiles: the percentiles used to calculate the final values and uncertainties
                       used as argument for np.percentile()
   :type percentiles: list
   :param return_chain: if true, the whole Markov chain is returned, otherwise on the 
                        values and errors (lower and upper) for the parameters
   :type return_chain: bool
   :returns: array (#parameters, #walkers * #steps) -- all samples taken by each walker.
   """
   
   #-- convert limits to keyword arguments for prepare_grid
   lim_kwargs = {}
   if not limits is None:
      for p, l in zip(models.parameters, limits):
         lim_kwargs[p+'_lim'] = l
   
   if 'grid' in kwargs:
      grid = kwargs.pop('grid')
   else:
      grid = models.prepare_grid(evolution_model=model, variables=variables,
                              set_default=True, **lim_kwargs)
      
   #-- set this grid as the default one
   models.defaults=grid
   
   #-- It is possible that the grid point do not directly correspond with
   #   the given limits. to avoid out of grid errors, we adapt the limits
   #   to the real grid points.
   limits = [(np.min(n),np.max(n)) for n in grid[0]]
   print "New limits to match up with grid points:"
   print limits
   
   #-- initialize the walkers
   #   Here we initialize them at random within the allowed ranges
   #   But we take random ages in yrs instead of in log(yrs) to prevent oversampling 
   #   young stars
   pos = [ np.random.uniform(lim[0], lim[1], nwalkers) for lim in limits]
   if 'log_Age' in models.parameters:
      i = models.parameters.index('log_Age')
      a1, a2 = limits[i]
      pos[i] = np.log10(np.random.uniform(10**a1, 10**a2, nwalkers))
   pos = np.array(pos).T

   #-- setup the sampler
   ndim = len(models.parameters)
   sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(obs, obs_err, limits))
   
   #-- run the sampler
   sampler.run_mcmc(pos, nsteps)

   #-- remove first 50 steps and combine the results from the individual walkers
   samples = sampler.chain[:, 50:, :].reshape((-1, ndim))
      
   
   #-- calculate the values and uncertainties based on the 16th, 50th, and 84th percentiles
   #   or whatever percentiles are given by the user
   pc  = np.percentile(samples, percentiles, axis=0)
   results = [(v, e1, e2) for v, e1, e2 in zip(pc[1], pc[1]-pc[0], pc[2]-pc[1])]
   
   if return_chain:
      return results, samples
   
   return results

#}