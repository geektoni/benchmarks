'''
  @file nbc.py
  @author Marcus Edel

  Class to benchmark the mlpack Parametric Naive Bayes Classifier method.
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
from profiler import *

import shlex
import subprocess
import re
import collections

'''
This class implements the Parametric Naive Bayes Classifier benchmark.
'''
class NBC(object):

  ''' 
  Create the Parametric Naive Bayes Classifier benchmark instance, show some 
  informations and return the instance.
  
  @param dataset - Input dataset to perform Naive Bayes Classifier on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["MLPACK_BIN"], 
      verbose=True, debug=os.environ["MLPACK_BIN_DEBUG"]):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout
    self.debug = debug

    # Get description from executable.
    cmd = shlex.split(self.path + "nbc -h")
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False) 
    except Exception as e:
      Log.Fatal("Could not execute command: " + str(cmd))
    else:
      # Use regular expression pattern to get the description.
      pattern = re.compile(br"""(.*?)Required.*?options:""", 
          re.VERBOSE|re.MULTILINE|re.DOTALL)
      
      match = pattern.match(s)
      if not match:
        Log.Warn("Can't parse description", self.verbose)
        description = ""
      else:
        description = match.group(1)

      self.description = description

  '''
  Destructor to clean up at the end. Use this method to remove created files.
  '''
  def __del__(self):    
    Log.Info("Clean up.", self.verbose)
    filelist = ["gmon.out", "output.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Run valgrind massif profiler on the Parametric Naive Bayes Classifier method. 
  If the method has been successfully completed the report is saved in the 
  specified file.

  @param options - Extra options for the method.
  @param fileName - The name of the massif output file.
  @param massifOptions - Extra massif options.
  @return Returns False if the method was not successful, if the method was 
  successful save the report file in the specified file.
  '''
  def RunMemoryProfiling(self, options, fileName, massifOptions="--depth=2"):
    Log.Info("Perform NBC Memory Profiling.", self.verbose)

    if len(self.dataset) != 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    # Split the command using shell-like syntax.
    cmd = shlex.split(self.debug + "nbc -t " + self.dataset[0] + " -T " 
        + self.dataset[1] + " -v " + options)

    return Profiler.MassifMemoryUsage(cmd, fileName, self.timeout, massifOptions)



  def RunMetrics(self, labels, prediction):
    import numpy as np
    # The labels and the prediction parameter contains the filename for the file
    # that contains the true labels accordingly the prediction parameter contains
    # the filename of the classifier output. So we need to read in the data.
    labelsData = np.genfromtxt(labels, delimiter=',')
    predictionData = np.genfromtxt(prediction, delimiter=',')

    Log.Info('Run metrics...')
    # Perform the metrics with the data from the labels and prediction file ....

  '''
  Perform Parametric Naive Bayes Classifier. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform NBC.", self.verbose)

    # Here we check the dataset count. If the user specefies only two datasets
    # we can't proform a evaluation of the classifier but we can measure the 
    # runtime of the method. So we distinguish between the two cases.

    # The dataset value should be a list, that contains the filename of the
    # trainings set and the test set, and perhaps there is a third filename for
    # the classifier evaluation.

    # Check if the dataset list contains two or three datasets.
    if (len(self.dataset) != 2) and (len(self.dataset) != 3):
      Log.Fatal("This method requires two or three datasets.")      
      return -1

    # We use the first two files from the dataset list to perform the runtime 
    # evaluation. So we use 'self.dataset[0]' and 'self.dataset[1]'.
    # Split the command using shell-like syntax.
    cmd = shlex.split(self.path + "nbc -t " + self.dataset[0] + " -T " 
        + self.dataset[1] + " -v " + options)

    # Call the nbc method with the specified parameters.
    # Run command with the nessecary arguments and return its output as a byte
    # string. We have untrusted input so we disable all shell based features.
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False, 
          timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      Log.Warn(str(e))
      return -2
    except Exception as e:
      Log.Fatal("Could not execute command: " + str(cmd))
      return -1

    # Okay we have to check if we have enough datasets in the dataset list to 
    # perform the additional evaluations.
    if len(self.dataset) == 3:
      # The predicted labels for the test set will be written to the output.csv 
      # file if we dosen't specify the '--output (-o)' option. So the file 
      # should located in the benchmark root directory as 'output.csv' file. So 
      # we can use the nbc output file and the true labels from the test 
      # dataset. The name of the file that contains the true labels should be
      # self.dataset[2].
      self.RunMetrics(self.dataset[2], 'output.csv')


    # Return the elapsed time.
    timer = self.parseTimer(s)
    if not timer:
      Log.Fatal("Can't parse the timer")
      return -1
    else:
      time = self.GetTime(timer)
      Log.Info(("total time: %fs" % (time)), self.verbose)

      # Check if we have to return a combination of time and metric information
      # or just the time.
      if len(self.dataset) == 3:
        # The metrics paramater is a object that we can handel in the main
        # benchmark loop (e.g. store the results into the database).
        #return (time, metrics)

        # We can't return (time, metrics) at this momemnt because we have to 
        # modify the main benchmark loop do work in the correct way.
        return time
      else:
        return time

  '''
  Parse the timer data form a given string.

  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data or -1 in case of an error.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.compile(br"""
        .*?testing: (?P<testing>.*?)s.*?
        .*?training: (?P<training>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)
    
    match = pattern.match(data)
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["testing", "training"])

      return timer(float(match.group("testing")),
          float(match.group("training")))

  '''
  Return the elapsed time in seconds.

  @param timer - Namedtuple that contains the timer data.
  @return Elapsed time in seconds.
  '''
  def GetTime(self, timer):
    time = timer.testing + timer.training
    return time