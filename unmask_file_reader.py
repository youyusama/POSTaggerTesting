import io
from config import *

class Unmask_File_Reader:
  def __init__(self, unmask_filename):
    self.unmask_file = io.open(unmask_filename, "r", encoding="utf-8")

  def __iter__(self):
    return self

  def __next__(self):
    line = self.unmask_file.readline()
    if line:
      unmask_struct = {'sen': line.strip('\n')}
      unmask_struct['id'] = int(self.unmask_file.readline().strip('\n'))
      unmask_struct['word'] = self.unmask_file.readline().strip('\n')
      unmask_struct['score'] = float(self.unmask_file.readline().strip('\n'))
      return unmask_struct
    else:
      raise StopIteration


def reader_skip_sen(reader, sen):# sen is PTF_sen for there are (do don't n't) 3 len in conllu but its 2 len
  for i in range(len(sen.words)-1):
    for j in range(UNMASK_NUM):
      next(reader)
  return


def reader_mut(reader, sen):
  unmasks = []
  for i in range(len(sen.words)-1):
    for j in range(UNMASK_NUM):
      unmasks.append(next(reader))
  return unmasks