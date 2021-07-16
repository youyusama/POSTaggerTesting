from PTF_Sen import *
import conllu
import io
import time
import os

#corpus = /mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu
def bert_gen_or_read(corpus):
  gen_filename = 'gen_data/bert-' + corpus.split('/')[-1].split('.')[0] + '.txt'
  if os.path.exists(gen_filename):
    return gen_filename
  else:
    outputfile = io.open(str(gen_filename), "w+", encoding="utf-8")
    #load corpus
    corpus = io.open(corpus, "r", encoding="utf-8")
    sen_num = 0
    for sen in conllu.parse_incr(corpus):
      print('unmask sentence ', sen_num)
      sen_num += 1
      sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
      list_info = sen_conllu.mutation_bert_insert_word_just_gen()
      for sen_info in list_info:
        for info in sen_info:
          outputfile.write(str(info) + '\n')
    return gen_filename
  

if __name__ == '__main__':
  bert_gen_or_read('/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu')