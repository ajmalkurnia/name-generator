from logging import raiseExceptions
import numpy as np

import random
import pickle

from collections import defaultdict, Counter
from itertools import product
import gzip

class MarkovGenerator:
  def __init__(self, n):
    self.n = n

    self.ngram = defaultdict(list)
    self.frequency_table = None
    self.probability_table = None
    self.vocab = set(["$", "#"])
    self.v2i = dict()
    self.g2i = dict()
    self.lite = False

  def add_gram(self, gram, next_state):
    if gram not in self.g2i:
      self.g2i[gram] = len(self.g2i)
    self.ngram[self.g2i[gram]].append(next_state)

  def add_the_rest_gram(self):
    non_terminal_vocab = self.vocab - set(["$", "#"])
    for i in range(1, self.n+1):
      all_gram = product(list(non_terminal_vocab), repeat=i)
      for gram in all_gram:
        gr = "$"*(self.n-i) + "".join(gram)
        if gr not in self.g2i:
          self.g2i[gr] = len(self.g2i)

  def fit(self, corpus, smooth=True):
    if self.lite:
      raise ValueError("Lite model cannot be updated")

    for doc in corpus:
      self.vocab |= set(doc)
      for idx in range(self.n):
        start = "$"*(self.n-idx) + doc[:idx+1]
        self.add_gram(start[:self.n], start[-1])
      for idx in range(len(doc)-self.n):
        self.add_gram(doc[idx:idx+self.n],doc[idx+self.n])
      self.add_gram(doc[-(self.n):], "#")

    if self.v2i:
      for v in sorted(list(self.vocab)):
        if v not in self.v2i:
          self.v2i[v] = len(self.v2i)
    else:
      self.v2i = {v: i for i, v in enumerate(sorted(list(self.vocab)))}
    self.i2v = {i: v for i, v in enumerate(sorted(list(self.v2i)))}
    valid_gram = set()

    if smooth:
      # Insert Other valid ngram to g2i
      self.add_the_rest_gram()
      self.probability_table = np.ones(
          (len(self.g2i), len(self.vocab)), dtype=np.int32)
      self.probability_table[:, self.v2i["$"]] = 0
      self.probability_table = np.cumsum(
          self.probability_table / len(self.vocab)-1, 1
      )
    else:
      self.probability_table = np.zeros(
          (len(self.g2i), len(self.vocab)), dtype=np.float32)
  
    for gram_idx, next_list in self.ngram.items():
      valid_gram.add(gram_idx)
      counter = Counter(next_list)
      frequency_table = np.full(
          (len(self.vocab),), int(smooth), dtype=np.int32)
      frequency_table[self.v2i["$"]] = 0

      for ch, freq in counter.items():
        frequency_table[self.v2i[ch]] += freq
      self.probability_table[gram_idx] = np.cumsum(
          frequency_table /
          (len(next_list)+int(smooth)*(len(self.vocab)-1))
      )

  def generate(self, seed="", max_length=100, max_words=99999):
    current_state = "$"*(self.n-len(seed)) + seed
    generated_string = seed
    white_space_counter = 0
    while (
      (current_state[-1] != "#") and
      (len(generated_string) <= max_length)
    ):
      rng = random.random()
      char_idx = np.argmax(self.probability_table[self.g2i[current_state]] > rng)
      char = self.i2v[char_idx]
      if char == " ":
        white_space_counter += 1
        if white_space_counter >= max_words:
          char = "#"
      if char != "#":
        generated_string += char
      current_state = current_state[1:] + char
    return generated_string
      
  def save(self, fname, lite=False):
    param_to_save = {
      "probability_table": self.probability_table,
      "n": self.n,
      "g2i": self.g2i,
      "i2v": self.i2v,
      "vocab": set(),
      "model": defaultdict(list),
      "v2i": dict(),
      "lite_mode": lite
    }
    if lite:
      with gzip.open(fname, "wb+") as f:
        pickle.dump(param_to_save, f)
      return

    param_to_save["model"] = self.ngram
    param_to_save["v2i"] = self.v2i
    param_to_save["vocab"] = self.vocab
    with open(fname, "wb") as f:
      pickle.dump(param_to_save, f)

  @staticmethod
  def load(fname):
    try:
      with open(fname, "rb") as f:
        data = pickle.load(f)
    except pickle.UnpicklingError:
      with gzip.open(fname, "rb") as f:
        data = pickle.load(f)
    markov = MarkovGenerator(data["n"])
    markov.ngram = data["model"]
    markov.vocab = data["vocab"]
    markov.probability_table = data["probability_table"]
    markov.v2i = data["v2i"]
    markov.i2v = data["i2v"]
    markov.g2i = data["g2i"]
    return markov