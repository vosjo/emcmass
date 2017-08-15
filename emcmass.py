 

import numpy as np

import emcee

import models

#{ Define the probability funtions

def lnlike(theta, y, yerr, **kwargs):
   """
   log likelihood function
   
   There is no need to check for limits in the likelihood function because
   this is already done in the prior function
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
   """
   
   for val, lim in zip(theta, limits):
      if val < lim[0] or val > lim[1]:
         return -np.inf
   
   return 0
   
def lnprob(theta, y, yerr, limits, **kwargs):
   """
   full log probability function combining the prior and the likelihood
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
         nwalkers=100, nsteps=1000):
   
   #-- convert limits to keyword arguments for prepare_grid
   lim_kwargs = {}
   if not limits is None:
      for p, l in zip(parameters, limits):
         lim_kwargs[p+'_lim'] = l
   
   grid = models.prepare_grid(parameters=parameters, variables=variables,
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
   
   return samples

#}

if __name__=="__main__":
   
   import sys
   import argparse
   import corner
   import pylab as pl
   
   parameters = ['initial_mass', 'log10_age_yr', 'feh']
   limits = None
   
   parser = argparse.ArgumentParser()
   parser.add_argument("-model", type=str, dest='model', default='mist_vvcrit0.0',
                       help="name of the stellar evolution model grid to use")
   parser.add_argument("-nwalkers", type=int, dest='nwalkers', default=100,
                       help="number of walkers in MCMC")
   parser.add_argument("-nsteps", type=int, dest='nsteps', default=1000,
                       help="number of steps each walker takes")
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
   
   print "Parameters of the model:"
   print "   ", parameters, "\n"
   
   print "Observables included in fit:"
   for v, y_, e_ in zip(variables, y, yerr):
      print "   {} = {} +- {}".format(v, y_, e_)
   print ""
   
   print "MCMC setup:"
   print "   # walkers:", args.nwalkers
   print "   # steps:", args.nsteps, "\n"
   
   
   print "================================================================================"
   
   samples = MCMC(parameters, variables, limits, y, yerr, 
         nwalkers=args.nwalkers, nsteps=args.nsteps)
   
   # create plot of the results
   
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
                              r"$\boldsymbol{ \log({\rm age}) }$ (yr)", 
                              "[Fe/H] (dex)"],
                     quantiles=[0.16, 0.5, 0.84],
                     show_titles=True, title_kwargs={"fontsize": 12})

   pl.show()