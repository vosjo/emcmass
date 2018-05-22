 
import numpy as np
import pylab as pl
import matplotlib.patches as patches

import models

def get_label(par):
   
   if par.lower() == 'mass_init':
      return r"Mi (M$_{\odot}$)"
   elif par.lower() == 'm_h_init':
      return '[M/H]i (dex)'
   elif par.lower() == 'phase':
      return 'EEP'
   elif par.lower() == 'age':
      return 'Age (yr)'
   
   else:
      return par
   
   
def plot_fit(variables, y, yerr, samples, results):
   
   obs = {}
   for v, y_, e_ in zip(variables, y, yerr):
      obs[v] = [y_, e_]
      
   pars = list(models.defaults[2])
   pars.remove('age')
   
   
   
   for i, par in enumerate(pars):
   
      ax = pl.subplot(1, len(pars), i+1)
      
      pc = np.percentile(samples[par], [0.2, 16, 50, 84, 99.8])
      
      #-- plot 1 sigma range as box
      ax.add_patch(
         patches.Rectangle(
            (0.5, pc[1]),
            1.0,
            pc[3]-pc[1],
            fill=False 
         )
      )
         
      #-- plot best fit and 50 percentile fit
      pl.plot([0.5,1.5], [results[par][0], results[par][0]], '--r', lw=1.5)
      pl.plot([0.5,1.5], [results[par][1], results[par][1]], '-b', lw=1.5)
      
      #-- plot 3 sigma range as wiskers
      pl.plot([1.0, 1.0], [pc[0], pc[1]], '-k', lw=1.5, zorder=0)
      pl.plot([1.0, 1.0], [pc[3], pc[4]], '-k', lw=1.5, zorder=0)
      
      #pl.boxplot(samples[par], usermedians=usermedians)
      
      if par in obs:
         pl.errorbar([1], obs[par][0], yerr=obs[par][1], color='r', marker='x', mew=2, lw=2)
      
      ax.axes.get_xaxis().set_visible(False)
      
      pl.title(par)
   
   

def plot_HR(variables, y, yerr, results, result='pc'):
   
   # use model from 'best' results or 'pc' results
   resi = 0 if result == 'best' else 1
   
   data, phase = models.get_track(results['mass_init'][resi], results['M_H_init'][resi], as_recarray=True)
   
   obs = {}
   for v, y_, e_ in zip(variables, y, yerr):
      obs[v] = [y_, e_]
   
   
   if 'log_Teff' in obs:
      xlim = [obs['log_Teff'][0]-obs['log_Teff'][1] - 0.1, 
              obs['log_Teff'][0]+obs['log_Teff'][1] + 0.1]
   else:
      xlim = None
   xlim = None
   
   pl.subplot(311)
   pl.subplots_adjust(hspace=0)
   
   pl.plot(data['log_Teff'], data['log_g'])
   
   if 'log_Teff' in obs and 'log_g' in obs:
      pl.errorbar(obs['log_Teff'][0], obs['log_g'][0], 
                  xerr=obs['log_Teff'][1], yerr=obs['log_g'][1],
                  color='r', marker='o')
   elif 'log_Teff' in obs:
      pl.axvline(x=obs['log_Teff'][0], color='r', ls='-')
      pl.axvline(x=obs['log_Teff'][0]-obs['log_Teff'][1], color='r', ls='-')
      pl.axvline(x=obs['log_Teff'][0]+obs['log_Teff'][1], color='r', ls='-')
   elif 'log_g' in obs:
      pl.axvline(x=obs['log_g'][0], color='r', ls='-')
      pl.axvline(x=obs['log_g'][0]-obs['log_g'][1], color='r', ls='-')
      pl.axvline(x=obs['log_g'][0]+obs['log_g'][1], color='r', ls='-')
   
   if not xlim is None: pl.xlim(xlim)
   
   if 'log_g' in obs:
      pl.ylim([obs['log_g'][0]-obs['log_g'][1] - 0.5, 
               obs['log_g'][0]+obs['log_g'][1] + 0.5]) 
   
   pl.gca().invert_xaxis()
   pl.gca().invert_yaxis()
   
   pl.ylabel('log(g) (dex)')
   
   
   pl.subplot(312)
   
   pl.plot(data['log_Teff'], data['log_L'])
   
   if 'log_Teff' in obs and 'log_L' in obs:
      pl.errorbar(obs['log_Teff'][0], obs['log_L'][0], 
                  xerr=obs['log_Teff'][1], yerr=obs['log_L'][1],
                  color='r', marker='o')
   elif 'log_Teff' in obs:
      pl.axvline(x=obs['log_Teff'][0], color='r', ls='-')
      pl.axvline(x=obs['log_Teff'][0]-obs['log_Teff'][1], color='r', ls='-')
      pl.axvline(x=obs['log_Teff'][0]+obs['log_Teff'][1], color='r', ls='-')
   elif 'log_L' in obs:
      pl.axvline(x=obs['log_L'][0], color='r', ls='-')
      pl.axvline(x=obs['log_L'][0]-obs['log_L'][1], color='r', ls='-')
      pl.axvline(x=obs['log_L'][0]+obs['log_L'][1], color='r', ls='-')
   
   if not xlim is None: pl.xlim(xlim)
   
   if 'log_L' in obs:
      pl.ylim([obs['log_L'][0]-obs['log_L'][1] - 0.5, 
               obs['log_L'][0]+obs['log_L'][1] + 0.5]) 
   
   pl.gca().invert_xaxis()
   
   pl.ylabel('log(L/L$_{\odot}$)')
   
   
   pl.subplot(313)
   
   pl.plot(data['log_Teff'], data['log_R'])
   
   if 'log_Teff' in obs and 'log_R' in obs:
      pl.errorbar(obs['log_Teff'][0], obs['log_R'][0], 
                  xerr=obs['log_Teff'][1], yerr=obs['log_R'][1],
                  color='r', marker='o')
   elif 'log_Teff' in obs:
      pl.axvline(x=obs['log_Teff'][0], color='r', ls='-')
      pl.axvline(x=obs['log_Teff'][0]-obs['log_Teff'][1], color='r', ls='-')
      pl.axvline(x=obs['log_Teff'][0]+obs['log_Teff'][1], color='r', ls='-')
   elif 'log_R' in obs:
      pl.axvline(x=obs['log_R'][0], color='r', ls='-')
      pl.axvline(x=obs['log_R'][0]-obs['log_R'][1], color='r', ls='-')
      pl.axvline(x=obs['log_R'][0]+obs['log_R'][1], color='r', ls='-')
   
   if not xlim is None: pl.xlim(xlim)
   
   if 'log_R' in obs:
      pl.ylim([obs['log_R'][0]-obs['log_R'][1] - 0.5, 
               obs['log_R'][0]+obs['log_R'][1] + 0.5])
   
   pl.gca().invert_xaxis()
   
   pl.xlabel('log(Teff/K)')
   pl.ylabel('log(R/R$_{\odot}$)')