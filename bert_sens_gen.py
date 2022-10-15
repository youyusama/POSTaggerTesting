from PTF_Sen import *
import conllu
import io
import time
import os
from config import *
from progress.counter import Counter

def bert_gen_or_read(corpus):
  gen_filename = 'gen_data/bert-' + str(MUTATION_WAY) + '-' + corpus.split('/')[-1].split('.')[0] + str(UNMASK_NUM) +'.txt'
  if os.path.exists(gen_filename):
    return gen_filename
  else:
    outputfile = io.open(str(gen_filename), "w+", encoding="utf-8")
    #load corpus
    corpus = io.open(corpus, "r", encoding="utf-8")
    unmask_counter = Counter('Unmasking sentence: ')
    for sen in conllu.parse_incr(corpus):
      unmask_counter.next()
      sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
      if MUTATION_WAY == 'ADD':
        list_info = sen_conllu.mutation_bert_insert_word_just_gen()
      elif MUTATION_WAY == 'REP':
        list_info = sen_conllu.mutation_bert_replace_word()
      for sen_info in list_info:
        for info in sen_info:
          outputfile.write(str(info) + '\n')
    unmask_counter.finish()
    return gen_filename
  

if __name__ == '__main__':
  bert_gen_or_read('corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu')