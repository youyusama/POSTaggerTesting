import conllu
import io
import time

#load corpus
corpus = io.open(r'/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-test.conllu', "r", encoding="utf-8")
#create output file
noun_filename = 'noun_set' + '.txt'
outputfile = io.open(str(noun_filename), "w+", encoding="utf-8")

#noun set
noun_set = set()

for sentence_conllu in conllu.parse_incr(corpus):
  for word in sentence_conllu:
    if word['upos'] == 'NOUN':
      noun_set.add(word['lemma'])

for noun in noun_set:
  outputfile.write(noun+'\n')