 
import numpy as np
import pylab as pl

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
   
   
def plot_fit():
   
   pass

def plot_HR(variables, y, yerr, results):
   
   data = models.get_track(results['mass_init'], results['M_H_init'], as_recarray=True)
   
   obs = {}
   for v, y_, e_ in zip(variables, y, yerr):
      obs[v] = [y_, e_]
   
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
   
   pl.gca().invert_xaxis()
   
   pl.xlabel('log(Teff/K)')
   pl.ylabel('log(R/R$_{\odot}$)')