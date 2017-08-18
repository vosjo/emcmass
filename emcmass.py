 

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
   return np.log( np.exp(-chi2/2.) )


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

def MCMC(parameters, variables, limits, obs, obs_err, 
         model='mist', nwalkers=100, nsteps=1000, percentiles=[16, 50, 84], return_chain=False):
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
      for p, l in zip(parameters, limits):
         lim_kwargs[p+'_lim'] = l
   
   grid = models.prepare_grid(evolution_model=model,
                              parameters=parameters, variables=variables,
                              set_default=True, **lim_kwargs)
   
   #-- It is possible that the grid point do not directly correspond with
   #   the given limits. to avoid out of grid errors, we adapt the limits
   #   to the real grid points.
   limits = [(np.min(n),np.max(n)) for n in grid[0]]
   print "New limits to match up with grid points:"
   print limits
   
   #-- initialize the walkers
   #   Here we initialize them at random within the allowed ranges
   pos = [ np.random.uniform(lim[0], lim[1], nwalkers) for lim in limits]
   pos = np.array(pos).T

   #-- setup the sampler
   ndim = len(parameters)
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

if __name__=="__main__":
   
   import sys
   import argparse
   import pylab as pl
   
   parameters = ['Mass_init', 'M_H_init', 'log_Age']
   limits = None
   
   parser = argparse.ArgumentParser()
   parser.add_argument("-model", type=str, dest='model', default='mist',
                       help="name of the stellar evolution model grid to use")
   parser.add_argument("-nwalkers", type=int, dest='nwalkers', default=100,
                       help="number of walkers in MCMC")
   parser.add_argument("-nsteps", type=int, dest='nsteps', default=1000,
                       help="number of steps each walker takes")
   parser.add_argument("-mass", type=float, dest='mass_lim', nargs=2, default=(0.1, 5.0),
                       help="limit the search in mass")
   parser.add_argument("-M_H", type=float, dest='mh_lim', nargs=2, default=(-1.5, 0.5),
                       help="limit the search in [M/H]")
   parser.add_argument("-age", type=float, dest='age_lim', nargs=2, default=(4, 10.3),
                       help="limit the search in log(Age)")
   args, variables = parser.parse_known_args()
   
   print "================================================================================"
   print "                                   EMCMASS"
   print "================================================================================"
   print ""
   
   #-- parse the observables
   if len(variables) > 0 and len(variables)%3 == 0:
      variables = np.reshape(variables, (-1, 3))
      y = np.array(variables[:,1], dtype=float)
      yerr = np.array(variables[:,2], dtype=float)
      variables = variables[:,0]
      
   elif len(variables) > 0:
      print "Could not understand observables!"
      sys.exit()
   
   else:
      # using default variables and requesting values on commandline
      print "Please specify the Observables below:"
      variables = ['log_L', 'log_Teff', 'log_g', 'feh']
      y, yerr = [], []
      for var in variables:
         val = raw_input("{} (value, err): ".format(var))
         val = val.split(',')
         y.append( float(val[0]) )
         yerr.append( float(val[1]) )
      
      y, yerr = np.array(y), np.array(yerr)
   
   print "Stellar evolution models: ", args.model, "\n"
   
   # parse the limits
   limits = [args.mass_lim, args.mh_lim, args.age_lim]
   print "Limits applied to the model grid parameters:"
   for p, l in zip(parameters, limits):
      print "   {} = {} -> {}".format(p, l[0], l[1])
   print ""
   
   print "Observables included in fit:"
   for v, y_, e_ in zip(variables, y, yerr):
      print "   {} = {} +- {}".format(v, y_, e_)
   print ""
   
   print "MCMC setup:"
   print "   # walkers:", args.nwalkers
   print "   # steps:", args.nsteps, "\n"
   
   
   print "================================================================================"
   
   results, samples = MCMC(parameters, variables, limits, y, yerr, return_chain=True,
                  model=args.model, nwalkers=args.nwalkers, nsteps=args.nsteps)
   
   print "================================================================================"
   print ""
   print "Resulting parameters values and errors:"
   for p, r in zip(parameters, results):
      print "   {} = {:0.3f} -{:0.3f} +{:0.3f}".format(p, r[0], r[1], r[2])
   
   
   # create plot of the results if the corner package exists
   try:
      import corner
   except Exception, e:
      sys.exit()
   
   params = {'backend': 'pdf',
   'ps.usedistiller': 'xpdf',
   'font.family': 'cm',
   'mathtext.fontset': 'cm',
   'text.latex.preamble':[r"\usepackage{amsmath}"], # to use \boldsymbol{} in mathtext
   'font.size' : 9,
   'axes.labelsize': 12,
   'legend.fontsize': 9,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'axes.linewidth': 1.0,
   'text.usetex': True,
   'figure.dpi': 100
   }
   pl.rcParams.update(params)

   fig = corner.corner(samples, 
                     labels=[r"Mass ($\boldsymbol{ M_{\odot} }$)", 
                             "[Fe/H] (dex)",
                             r"$\boldsymbol{ \log({\rm age}) }$ (yr)", 
                             ],
                     quantiles=[0.16, 0.5, 0.84],
                     show_titles=True, title_kwargs={"fontsize": 12})

   pl.show()