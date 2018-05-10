import sys
import argparse

import pylab as pl
import numpy as np

import emcee

import models, mcmc

import mcmc

if __name__=="__main__":
   
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
   parser.add_argument("-age", type=float, dest='age_lim', nargs=2, default=(0, 400),
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
      variables = np.array(variables[:,0], dtype='a10')
      
   elif len(variables) > 0:
      print "Could not understand observables!"
      sys.exit()
   
   else:
      # using default variables and requesting values on commandline
      print "Please specify the Observables below:"
      variables = ['log_L', 'log_Teff', 'log_g', 'log_R', 'feh']
      y, yerr = [], []
      for var in variables:
         val = raw_input("{} (value, err): ".format(var))
         if val == '': continue
         val = val.split(',')
         y.append( float(val[0]) )
         yerr.append( float(val[1]) )
      
      y, yerr = np.array(y), np.array(yerr)
      
      
   #-- check if variables need to be converted to log(variable)
   for par in ['L', 'R', 'Teff', 'g']:
      if par in variables:
         i = np.where(variables == par)
         variables[i] = 'log_'+par
         yerr[i] = 0.434 * yerr[i] / y[i]
         y[i] = np.log10(y[i])
   
   print "Stellar evolution models: ", args.model, "\n"
   
   # parse the limits
   limits = [args.mass_lim, args.mh_lim, args.age_lim]
   print "Limits applied to the model grid parameters:"
   for p, l in zip(models.parameters, limits):
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
   
   results, samples = mcmc.MCMC(variables, limits, y, yerr, return_chain=True,
                  model=args.model, nwalkers=args.nwalkers, nsteps=args.nsteps)
   
   print "================================================================================"
   print ""
   print "Resulting parameters values and errors:"
   for p, r in zip(models.parameters, results):
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