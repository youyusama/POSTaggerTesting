import stanza
import conllu
import io
import time
import random
from sen_pos import SenPos, compare_sen_pos

#load corpus
corpus = io.open(r'/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-test.conllu', "r", encoding="utf-8")
#load stanza
nlp = stanza.Pipeline('en', r'/mnt/hd0/POStaggingFuzzing/nlp-models/stanzamodel/stanza_model/', processors='tokenize,pos', tokenize_pretokenized=True)
#create output file
outputfile = io.open('results/good_sample_sentences.txt', "w+", encoding="utf-8")

for sentence_conllu in conllu.parse_incr(corpus):
  sen_conllu = SenPos(sentence_conllu)
  sen_stanza = SenPos(nlp(sen_conllu.to_doc()).sentences[0], sen_type='stanza')
  if len(compare_sen_pos(sen_conllu, sen_stanza)) == 0:
    if len(sen_conllu.sen) >= 10 and len(sen_conllu.sen) <=20:
      outputfile.write(sen_conllu.to_doc() + '\n')