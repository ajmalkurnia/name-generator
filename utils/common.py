import csv
import logging
from time import time


def read_vocab(fname):
  data = []
  with open(fname, "r") as f:
    for line in f:
      line = line.strip()
      if line:
        data.append(line)
  return data


def read_csv(fname):
  data = []
  with open(fname, "r") as f:
    csvr = csv.reader(f)
    for row in csvr:
      data.append(row)
  return data


def measure_time(func, *args, **kwargs):
  start_time = time()
  return_value = func(*args, **kwargs)
  print(f"Elapsed time: {time()-start_time}")
  return return_value
