'''
  @file lars.py
  @author Marcus Edel

  Least Angle Regression with scikit.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from timer import *

import numpy as np
from sklearn.linear_model import LassoLars

'''
This class implements the Least Angle Regression benchmark.
'''
class LARS(object):

  ''' 
  Create the Least Angle Regression benchmark instance.
  
  @param dataset - Input dataset to perform Least Angle Regression on.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, verbose=True): 
    self.verbose = verbose
    self.dataset = dataset

  '''
  Destructor to clean up at the end.
  '''
  def __del__(self):
    pass

  '''
  Use the scikit libary to implement Least Angle Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def LARSScikit(self, options):
    totalTimer = Timer()

    # Load input dataset.
    Log.Info("Loading dataset", self.verbose)
    inputData = np.genfromtxt(self.dataset[0], delimiter=',')
    responsesData = np.genfromtxt(self.dataset[1], delimiter=',')

    with totalTimer:
      # Get all the parameters.
      lambda1 = re.search("-k (\d+)", options)
      if not lambda1:
        lambda1 = 0.
      else:
        lambda1 = int(lambda1.group(1))

      # Perform LARS.
      model = LassoLars(alpha=lambda1)
      model.fit(inputData, responsesData)
      out = model.coef_

    return totalTimer.ElapsedTime()

  '''
  Perform Least Angle Regression. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform LARS.", self.verbose)

    return self.LARSScikit(options)