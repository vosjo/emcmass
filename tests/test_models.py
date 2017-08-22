import numpy as np

import  unittest

from emcmass import models

class TestGetFiles(unittest.TestCase):
   
   def test_mist_files(self):
      
      files, z = models.get_files('mist')
      
      self.assertTrue(-4.0 in z)
      self.assertTrue(0.5 in z)
      
      for filename in files:
         self.assertTrue('MIST' in filename)
   
   def test_yapsi_files(self):
      
      files, z = models.get_files('yapsi')
      
      self.assertTrue(-1.5 in z)
      self.assertTrue(0.3 in z)
      
      for filename in files:
         self.assertTrue('YaPSI' in filename)
   
class TestPrepareGrid(unittest.TestCase):
   
   def setUp(self):
      models.defaults = None # clear the default grid
      self.evolution_model = 'mist'
      self.variables = ['log_L', 'log_Teff', 'log_g', 'M_H']
      self.limits = [(0.5, 1.25), (-0.5, 0.5), (6.5, 8.0)]
      
      lim_kwargs = {}
      for p, l in zip(models.parameters, self.limits):
         lim_kwargs[p+'_lim'] = l
      
      axis_values, pixelgrid = models.prepare_grid(evolution_model=self.evolution_model,
                                       variables=self.variables,
                                       set_default=True, **lim_kwargs)
      
      self.axis_values = axis_values
      self.pixelgrid = pixelgrid
   
   def test_included_variables(self):     
      self.assertEqual(self.pixelgrid.shape[-1], 4, )
      self.assertEqual(len(self.axis_values), len(models.parameters))
      
   def test_limits(self):
      for p, lim, val in zip(models.parameters, self.limits, self.axis_values):
         self.assertTrue(np.min(val) >= lim[0])
         self.assertTrue(np.max(val) <= lim[1])
      
   
   def test_set_defaults(self):
      self.assertTrue(np.all(models.defaults[1] == self.pixelgrid))
      
      for g1, g2 in zip(models.defaults[0], self.axis_values):
         self.assertTrue(np.all(g1 == g2))
      

class TestInterpolate(unittest.TestCase):
   
   def setUp(self):
      models.defaults = None # clear the default grid
      self.evolution_model = 'mist'
      self.variables = ['log_L', 'log_Teff', 'log_g', 'M_H']
   
   def test_grid_point(self):
      
      values = models.interpolate(1.0, -0.25, 5.5, 
                                  evolution_model = self.evolution_model, 
                                  variables=self.variables)
      
      expected = [0.71038623, 3.66646819, 3.34812825, -0.2593401]
      
      for var, v1, v2 in zip(self.variables, values, expected):
         self.assertAlmostEqual(v1, v2, places=3, 
                                msg="Wrong value for {}, {} != {} in 3 places".format(var, v1, v2))
         
   def test_non_grid_point(self):
      
      values = models.interpolate(1.23, -0.125, 5.342, 
                                 evolution_model = self.evolution_model, 
                                 variables=self.variables)
      
      expected = [0.9616026, 3.66988543, 3.2004471, -0.12966358]
      
      for var, v1, v2 in zip(self.variables, values, expected):
         self.assertAlmostEqual(v1, v2, places=3,
                                msg="Wrong value for {}, {} != {} in 3 places".format(var, v1, v2))

class TestGetIsochrone(unittest.TestCase):
   
   def setUp(self):
      models.defaults = None # clear the default grid
      self.evolution_model = 'mist'
      self.variables = ['log_L', 'log_Teff', 'log_g', 'M_H']
      
   def test_grid_point(self):
      
      values = models.get_isochrone(-0.25, 6.5,
                                    evolution_model = self.evolution_model, 
                                    variables=self.variables)
      
      expected = [-1.47366179, 3.49777507, 3.85755361, -0.259340103]
      
      self.assertEqual(values.shape[0], len(self.variables), 
                       msg="Returned amount of variables is wrong, {} != {}".format(values.shape[0], len(self.variables)) )
      
      #-- only test the first values in the list
      for var, v1, v2 in zip(self.variables, values, expected):
         self.assertAlmostEqual(v1[0], v2, places=3,
                                msg="Wrong value for {}, {} != {} in 3 places".format(var, v1, v2))
      
   def test_non_grid_point(self):
      
      values = models.get_isochrone(-0.17, 6.536,
                                    evolution_model = self.evolution_model, 
                                    variables=self.variables)
      
      expected = [-1.51310257, 3.49048494, 3.86783385, -0.17634713]
      
      self.assertEqual(values.shape[0], len(self.variables), 
                       msg="Returned amount of variables is wrong, {} != {}".format(values.shape[0], len(self.variables)) )
      
      #-- only test the first values in the list
      for var, v1, v2 in zip(self.variables, values, expected):
         self.assertAlmostEqual(v1[0], v2, places=3,
                                msg="Wrong value for {}, {} != {} in 3 places".format(var, v1, v2))

if __name__ == '__main__':
   unittest.main()