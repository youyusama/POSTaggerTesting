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
filename = time.strftime("results/w2v-mutation%Y%m%d-%H%M%S-",time.localtime())+'.txt'
outputfile = io.open(str(filename), "w+", encoding="utf-8")

#config
MUTATION_NUM = 10
#filter output
filtered_tag = ('PRON', 'PROPN')

mutation_sen_num = 0
mutation_tag_change = 0
for sentence_conllu in conllu.parse_incr(corpus):
  origin_sen_conllu = SenPos(sentence_conllu, 'conllu')
  origin_sen_stanza = SenPos(nlp(origin_sen_conllu.to_doc()).sentences[0], 'stanza')
  # og_wrong = compare_sen_pos(origin_sen_conllu, origin_sen_stanza)
  #mutation
  mutation_sens, noun_i = origin_sen_conllu.mutation_noun_w2v(MUTATION_NUM)
  mutation_sens_nlp = nlp(mutation_sens).sentences
  for i in range(len(noun_i)*MUTATION_NUM):
    mutated_sen_stanza = SenPos(mutation_sens_nlp[i], 'stanza')
    os_ms_change = compare_sen_pos(origin_sen_stanza, mutated_sen_stanza)
    mutation_tag_change += len(os_ms_change)
    if len(os_ms_change) > 0:
      for change in os_ms_change:
        if change[0] == noun_i[i//MUTATION_NUM] and change[2] not in filtered_tag:
          outputfile.write('noun identify wrong: ' + str(change) + '\n')
        elif change[0] != noun_i[i//MUTATION_NUM]:
          outputfile.write('other pos identify wrong: ' + str(change) + '\n')
      outputfile.write('original sentence: ' + origin_sen_conllu.to_doc() + '\n')
      outputfile.write('mutated sentence:  ' + mutated_sen_stanza.to_doc() + '\n')
      outputfile.write('---------------------------------------\n')

print('tag change num: ' , mutation_tag_change)