 
import numpy as np
import pylab as pl

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