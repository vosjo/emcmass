 
import numpy as np

import  unittest

from emcmass import models, emcmass

class TestMCMC(unittest.TestCase):
   
   def setUp(self):
      
      self.evolution_model = 'mist'
      self.variables = ['log_L', 'log_Teff', 'log_g', 'M_H']
      self.limits = [(0.2, 1.1), (-1.0, 0.25), (5.0, 9.0)]
      self.obs = np.array([-0.55, 3.67, 4.50, -0.35])
      self.obs_err = np.array([0.15, 0.05, 0.50, 0.40])
      
   def test_mcmc_mist(self):
   
      results = emcmass.MCMC(self.variables, self.limits, self.obs, self.obs_err,
                     model='mist', nwalkers=100, nsteps=1000, percentiles=[16, 50, 84], 
                     return_chain=False)
   
      
      values = [0.75, -0.32, 7.57]
      value_ers = [0.03, 0.05, 1.0]
      
      
      for par, r, v, e in zip(models.parameters, results, values, value_ers):
         self.assertLess(np.abs(r[0]-v), e, 
                         msg="MCMC result for {} not within error: {} != {} within {}".format(par, r[0], v, e))
      
            
      errors = [0.10, 0.33, 1.0]
      errors_ers = [0.05, 0.1, 0.5]
      
      for par, r, v, e in zip(models.parameters, results, errors, errors_ers):
         self.assertLess(np.abs(r[1]-v), e, 
                         msg="MCMC uncertainty for {} not within error: {} != {} within {}".format(par, r[1], v, e))
         
         self.assertLess(np.abs(r[2]-v), e, 
                         msg="MCMC uncertainty for {} not within error: {} != {} within {}".format(par, r[2], v, e))
      
      