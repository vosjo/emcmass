
import numpy as np

import os
import re 
import glob
import pyfits

import interpol

defaults = None
parameters = ['mass_init', 'M_H_init', 'phase']

basedir = os.path.dirname(__file__)

def get_files(evolution_model):
   """
   Returns list of files belonging to the requested evolution models together
   with a list of the metalicity of each file
   
   curently recognized models are: 
    - mist: MESA Isochrones & Stellar tracks with v/vcrit = 0.0
    - yapsi: Yale Potsdam Stellar Isochrones
   """
   
   modeldir = os.path.join(basedir, 'Models')
   
   if evolution_model == 'mist':
      filename = 'MIST_vvcrit0.0_feh_*.fits'
   
   elif evolution_model == 'yapsi':
      filename = 'YaPSI_feh_*.fits'
   
   else:
      # default to MIST if models not recognized
      filename = 'MIST_vvcrit0.0_feh_*.fits'
   
   files = glob.glob(os.path.join(basedir, 'Models', filename))
   
   files = sorted(files)
   
   # exctract metalicity from name
   z = np.zeros_like(files, dtype=float)
   for i, f in enumerate(files):
      sign, z_ = re.findall('([mp])(\d\.\d\d)', f)[0]
      z[i] = float(z_) * -1 if sign == 'm' else float(z_)
   
   return files, z

def prepare_grid(evolution_model='mist',
                 variables=['log_L', 'log_Teff', 'log_g', 'M_H'],
                 parameters=['mass_init', 'M_H_init', 'phase'],
                 set_default=False, 
                 **kwargs):
   """
   Prepares the stellar evolution models by creating a pixelgrid to be used in interpolate
   This method will read the stellar evolution models from file, select only 
   the columns you want to interpolate over (given in parameter_names), and will 
   return axis_values, pixelgrid to be used in interpolate. 
   
   You can also provide limits on the size of the grid in mass, feh and age by
   setting the mass_lim, feh_lim and age_lim keywords
   
   """
   
   files, fehs = get_files(evolution_model)
   
   grid_pars = []
   grid_vars = []
   
   fehlim = kwargs.pop('M_H_lim', (-np.inf, np.inf))
   
   for filename, z in zip(files, fehs):
      
      #-- skip the file if it is out of metalicity range
      if z < fehlim[0] or z > fehlim[1]: continue
      
      data = pyfits.getdata(filename)
      
      keep = np.ones(len(data),bool)
      
      #-- run over all provided kwargs to check if any limitations on the grid
      #   are requested, and apply them. Limits can be given for any parameter
      #   in the grid.
      for key in kwargs:
         if not '_lim' in key: continue
         
         low, high = kwargs[key][0], kwargs[key][1]
         key = key.replace('_lim', '')
         in_range = (low<=data[key]) & (data[key]<=high)
      
         keep = keep & in_range
      data = data[keep]
      
      #-- only keep the parameters and variables that are needed to reduce memory
      pars_ = np.vstack([data[name] for name in parameters])
      vars_ = np.vstack([data[name] for name in variables])
      
      if sum(keep):
         grid_pars.append(pars_)
         grid_vars.append(vars_)
   
   grid_pars = np.hstack(grid_pars)
   grid_vars = np.hstack(grid_vars)
   
   axis_values, pixelgrid = interpol.create_pixeltypegrid(grid_pars, grid_vars)
   
   if set_default:
      #-- store the prepared pixel grid to be used by interpolation functions
      global defaults
      defaults = (axis_values, pixelgrid, parameters, variables)
   
   return axis_values, pixelgrid, variables
         

def interpolate(mass, feh, phase, **kwargs):
   """
   Returns the requested values from the stellar evolution grids at the given 
   values for the input parameters (mass, feh, phase)
   
   """
   
   global defaults
   if 'grid' in kwargs:
      axis_values, pixelgrid, variables = kwargs['grid']
   elif not defaults is None:
      axis_values, pixelgrid, variables = defaults
   else:
      axis_values, pixelgrid, variables = prepare_grid(**kwargs)
   
   multiple = False
   if not hasattr(mass, '__iter__') or not hasattr(phase, '__iter__') or \
      not hasattr(feh, '__iter__'):
      mass = np.array(mass)
      phase = np.array(phase)
      feh = np.array(feh)
      multiple = True
   
   p = np.vstack([mass, feh, phase])
   
   values = interpol.interpolate(p, axis_values, pixelgrid)
   
   if multiple:
      values = values.flatten()
   
   #-- convert values to a recarray if that is requested
   if kwargs.get('as_recarray', False):
      dtypes = [(name, 'f8') for name in variables]
      values = np.array(values, dtype=dtypes)
      
   return values

#def get_isochrone(feh, age, **kwargs):
   #"""
   #returns an isochrone for the requested metalicity and age
   #The mass points of the track are the gridpoints included in the evolution grid
   #"""
   
   ##-- get the mass values
   ##   if mass values are provided in kwargs it is easy, otherwise we need to get
   ##   the axis_values from the prepared pixel grid, which can be provided in the
   ##   grid keyword, in the defaults of the module, or in the last case needs to 
   ##   be calculated.
   ##   if the grid needs to be prepared, we store it and provide it in the grid 
   ##   kwarg to the interpolate function
   #global defaults
   #mass = None
   #if 'mass' in kwargs:
      #mass = kwargs.pop('mass')
   #elif 'grid' in kwargs:
      #axis_values, pixelgrid = kwargs['grid']
   #elif not defaults is None:
      #axis_values, pixelgrid = defaults
      #kwargs['grid'] = (axis_values, pixelgrid)
   #else:
      #axis_values, pixelgrid = prepare_grid(**kwargs)
      #kwargs['grid'] = (axis_values, pixelgrid)
   
   #mass = sorted(set(axis_values[0])) if mass is None else mass
   
   #age = np.ones_like(mass) * age
   #feh = np.ones_like(mass) * feh
   
   #return interpolate(mass, feh, age, **kwargs)

def get_track(mass, feh, **kwargs):
   """
   Returns an evolution track for a given mass and metalicity. 
   The age points of the track are the gridpoints included in the evolution grid
   """
   
   #-- get the age values
   #   if age values are provided in kwargs it is easy, otherwise we need to get
   #   the axis_values from the prepared pixel grid, which can be provided in the
   #   grid keyword, in the defaults of the module, or in the last case, needs to 
   #   be calculated.
   #   if the grid needs to be prepared, we store it and provide it in the grid 
   #   kwarg to the interpolate function
   global defaults
   phase = None
   if 'phase' in kwargs:
      phase = kwargs.pop('phase')
      
   if 'grid' in kwargs:
      axis_values, pixelgrid = kwargs['grid']
   elif not defaults is None:
      axis_values, pixelgrid = defaults
      kwargs['grid'] = (axis_values, pixelgrid)
   else:
      axis_values, pixelgrid = prepare_grid(**kwargs)
      kwargs['grid'] = (axis_values, pixelgrid)
   
   phase = sorted(set(axis_values[2])) if phase is None else phase
   
   mass = np.ones_like(phase) * mass
   feh = np.ones_like(phase) * feh
   
   return interpolate(mass, feh, phase, **kwargs)

if __name__=="__main__":

   grid1 = prepare_grid(evolution_model='mist',
                        variables=['log_L', 'log_Teff', 'log_g', 'M_H'],
                        phase_lim=(1.0, 4.0),
                        Mass_init_lim = (0.4, 2.6), 
                        M_H_init_lim = (-1.0, 0.5),
                        )

   #grid2 = prepare_grid(evolution_model='yapsi',
                        #variables=['log_L', 'log_Teff', 'log_g', 'M_H'],
                        #log_Age_lim=(5.0, 9.0),
                        #Mass_init_lim = (0.4, 2.6), 
                        #M_H_init_lim = (-1.0, 0.5),
                        #)
   
   
   print interpolate(1.23, 0.125, 1.5, grid=grid1)
   #print interpolate(1.23, 0.125, 6.37, grid=grid2)