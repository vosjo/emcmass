import sys
import yaml
import argparse

import pylab as pl
import numpy as np

import emcee

import models, mcmc, plotting


default = """
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
# The name of the evolution model to use (mist, yapsi)
model: mist
# setup for the MCMC algorithm
nwalkers: 100    # total number of walkers
nsteps: 2000     # steps taken by each walker (not including burn-in)
nrelax: 500      # burn-in steps taken by each walker
a: 10            # relative size of the steps taken
# set the percentiles for the error determination 
percentiles: [0.2, 50, 99.8] # 16 - 84 corresponds to 1 sigma
# output options
datafile: none   # filepath to write results of all walkers
plot1:
 type: fit
 path: ./results/<objectname>_fit.png
plot2:
 type: distribution
 path: ./results/<objectname>_distribution.png
 parameters: ['mass_init', 'phase', 'M_H_init']
plot3:
 type: HR
 path: ./results/<objectname>_HR.png
"""


if __name__=="__main__":
   
   parser = argparse.ArgumentParser()
   parser.add_argument("-f", type=str, dest='filename', default=None,
                       help="use the setup given in this yaml file")
   parser.add_argument("-empty", type=str, dest='defaultfile', default=None,
                       help="create a default setup file with the given name.")
   parser.add_argument("-model", type=str, dest='model', default='mist',
                       help="name of the stellar evolution model grid to use")
   parser.add_argument("-nwalkers", type=int, dest='nwalkers', default=100,
                       help="number of walkers in MCMC")
   parser.add_argument("-nsteps", type=int, dest='nsteps', default=1000,
                       help="number of steps each walker takes")
   parser.add_argument("-a", type=int, dest='a', default=2,
                       help="scaling factor for the step size")
   parser.add_argument("-mass", type=float, dest='mass_lim', nargs=2, default=(0.1, 5.0),
                       help="limit the search in mass")
   parser.add_argument("-M_H", type=float, dest='mh_lim', nargs=2, default=(-1.5, 0.5),
                       help="limit the search in [M/H]")
   parser.add_argument("-phase", type=float, dest='phase_lim', nargs=2, default=(0, 400),
                       help="limit the search in evolutionary phase")
   parser.add_argument("--plot", action='store_true', dest='plot', default=False,
                       help="Will show the default plots when fitting")
   args, variables = parser.parse_known_args()
   
   print "================================================================================"
   print "                                   EMCMASS"
   print "================================================================================"
   print ""
   
   if not args.defaultfile is None:
      
      objectname = args.defaultfile
      filename = objectname + '.yaml'
      
      out = default.replace('<objectname>', objectname)
      
      ofile = open(filename, 'w')
      ofile.write(out)
      ofile.close()
      print "Written default setup file to: " + args.defaultfile
      sys.exit()
   
   if not args.filename is None:
      # First check if there is a setup file given and use that to run.
      #================================================================
      
      setupfile = open(args.filename)
      setup = yaml.safe_load(setupfile)
      setupfile.close()
      
      parameters = setup.get('parameters', ['mass_init', 'M_H_init', 'phase'])
      limits = setup.get('limits', None)
      
      variables = np.array(setup['observables'].keys(), dtype='a10')
      y = np.array([setup['observables'][key][0] for key in variables])
      yerr = np.array([setup['observables'][key][1] for key in variables])
      
      model = setup.get('model', 'mist')
      
      mcmc_kws = dict(nwalkers=setup.get('nwalkers', 100),
                      nsteps=setup.get('nsteps', 1000),
                      a=setup.get('a', 2))
      
      percentiles = setup.get('percentiles', [16, 50, 84])
      
   else:
      # If no setup file is given, run from command line options.
      #==========================================================
      
      parameters = ['mass_init', 'M_H_init', 'phase'] 
      limits = [args.mass_lim, args.mh_lim, args.phase_lim]
      
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
         print "No observables given!"
         sys.exit()
      
      model = args.model
      
      mcmc_kws = dict(nwalkers=args.nwalkers,
                      nsteps=args.nsteps,
                      a=args.a)
         
      percentiles = [16, 50, 84]
   
   #-- set the parameters
   models.parameters = parameters
      
   #-- check if variables need to be converted to log(variable)
   for par in ['L', 'R', 'Teff', 'g']:
      if par in variables:
         i = np.where(variables == par)
         variables[i] = 'log_'+par
         yerr[i] = 0.43429 * yerr[i] / y[i]
         y[i] = np.log10(y[i])
   
   #-- print the setup
   print "Stellar evolution models: ", model, "\n"
   
   
   print "Limits applied to the model grid parameters:"
   for p, l in zip(parameters, limits):
      print "   {} = {} -> {}".format(p, l[0], l[1])
   print ""
   
   
   print "Observables included in fit:"
   for v, y_, e_ in zip(variables, y, yerr):
      print "   {} = {} +- {}".format(v, y_, e_)
   print ""
   
   
   print "MCMC setup:"
   print "   # walkers:", mcmc_kws['nwalkers']
   print "   # steps:", mcmc_kws['nsteps']
   print "   # a:", mcmc_kws['a']
   
   
   print "================================================================================"
   results, samples = mcmc.MCMC(variables, limits, y, yerr, return_chain=True,
                  model=model, **mcmc_kws)
   
   print "================================================================================"
   print ""
   print "Resulting parameters values and errors:"
   
   pc  = np.percentile(samples.view(np.float64).reshape(samples.shape + (-1,)), percentiles, axis=0)
   for p, v, e1, e2 in zip(samples.dtype.names, pc[1], pc[1]-pc[0], pc[2]-pc[1]):
      results[p] = [results[p], v, e1, e2]
   
   print "   Par          Best    Pc      emin     emax"
   for p in parameters:
      print "   {:10s} = {:0.3f}   {:0.3f}   -{:0.3f}   +{:0.3f}".format(p, *results[p])
      
   
   out = ""
   for par in ['mass_init', 'M_H_init']:
      out += "{:0.3f}\t{:0.3f}\t".format(results[par][1], 
                                         np.average([results[par][2],results[par][3]]))
   out += "{:0.0f}\t{:0.0f}\t".format(results['phase'][1], np.average([results['phase'][2],results['phase'][3]]))
   print out
   
   # create plot of the results if the corner package exists
   try:
      import corner
   except Exception, e:
      sys.exit()
   
   if not 'setup' in globals() and args.plot: 
      
      pars = []
      for p in ['mass_init', 'M_H_init', 'phase']:
         if p in samples.dtype.names: pars.append(p)
         
      data = samples[pars]

      fig = corner.corner(data.view(np.float64).reshape(data.shape + (-1,)), 
                  labels=[plotting.get_label(p) for p in data.dtype.names],
                  quantiles=[0.025, 0.16, 0.5, 0.84, 0.975],
                  levels=[0.393, 0.865, 0.95],
                  show_titles=True, title_kwargs={"fontsize": 12})
      
      pl.figure(2, figsize=(10, 6))
      pl.subplots_adjust(wspace=0.40, left=0.07, right=0.98)
      plotting.plot_fit(variables, y, yerr, samples, results)
      
      pl.figure(3, figsize=(6, 10))
      plotting.plot_HR(variables, y, yerr, results)
      
      pl.show()
      sys.exit()
   
   #-- Plotting 
   for i in range(10):
      
      pindex = 'plot'+str(i)
      if not pindex in setup: continue
   
      if setup[pindex]['type'] == 'distribution':
         
         pars = []
         for p in setup[pindex].get('parameters', ['mass_init', 'M_H_init', 'phase']):
            if p in samples.dtype.names: pars.append(p)
            
         data = samples[pars]

         fig = corner.corner(data.view(np.float64).reshape(data.shape + (-1,)), 
                     labels=[plotting.get_label(p) for p in data.dtype.names],
                     quantiles=setup[pindex].get('quantiles', [0.025, 0.16, 0.5, 0.84, 0.975]),
                     levels=setup[pindex].get('levels', [0.393, 0.865, 0.95]),
                     show_titles=True, title_kwargs={"fontsize": 12})
         
         if not setup[pindex].get('path', None) is None:
            pl.savefig(setup[pindex].get('path'))
      
      if setup[pindex]['type'] == 'HR':
         
         pl.figure(i, figsize=(6, 10))
         pl.subplots_adjust(left=0.14, right=0.97, top=0.97, bottom=0.07)
         plotting.plot_HR(variables, y, yerr, results, 
                          result=setup[pindex].get('result', 'pc'))
         
         if not setup[pindex].get('path', None) is None:
            pl.savefig(setup[pindex].get('path'))
            
      if setup[pindex]['type'] == 'fit':
         
         pl.figure(i, figsize=(10, 6))
         pl.subplots_adjust(wspace=0.40, left=0.07, right=0.98)
         plotting.plot_fit(variables, y, yerr, samples, results)
         
         if not setup[pindex].get('path', None) is None:
            pl.savefig(setup[pindex].get('path'))
      
   #params = {'backend': 'pdf',
   #'ps.usedistiller': 'xpdf',
   #'font.family': 'cm',
   #'mathtext.fontset': 'cm',
   #'text.latex.preamble':[r"\usepackage{amsmath}"], # to use \boldsymbol{} in mathtext
   #'font.size' : 9,
   #'axes.labelsize': 12,
   #'legend.fontsize': 9,
   #'xtick.labelsize': 12,
   #'ytick.labelsize': 12,
   #'axes.linewidth': 1.0,
   #'text.usetex': True,
   #'figure.dpi': 100
   #}
   #pl.rcParams.update(params)
   
   

   pl.show()