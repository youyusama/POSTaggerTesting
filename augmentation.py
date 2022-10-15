import csv
import stanza
from config import *
import random
from PTF_Sen import *
from progress.counter import Counter
import io
import conllu
from compare_utilities import *

sen_id = 0
f = open('mutant_corpus/argumentation_corpus2.conllu', mode='w+', encoding='utf-8')
def write_words(words):
  if len(words) == 0:
    return
  global sen_id
  f.write('# sent_id = mut' + str(sen_id) + '\n')
  f.write('# text = ' + ' '.join([word.text for word in words]) + '\n')
  w_id = 1
  for word in words:
    f.write(str(w_id)+'\t' + word.text + '\t' + word.lemma +'\t' +word.upos + '\t' + word.xpos + '\t' + '_\t'+ str(word.head) + '\t'+ '_\t'+ '_\t'+ '_\n')
    w_id += 1
  sen_id += 1
  f.write('\n')

def get_mutant(sen_conllu, sen_mut, mut_type):
  correct_words = []
  index_s = 0
  index_e = len(sen_mut.words)-1
  index_e_o = len(sen_conllu.words)-1
  while index_s < len(sen_mut.words) and index_s < len(sen_conllu.words) and sen_conllu.words[index_s].text == sen_mut.words[index_s].text:
    index_s += 1
  while index_e >= 0 and index_e_o >= 0 and sen_conllu.words[index_e_o].text == sen_mut.words[index_e].text:
    index_e -= 1
    index_e_o -= 1
  if mut_type == 'add':
    if index_s == index_e:
      correct_words = [word for word in sen_conllu.words]
      correct_words.insert(index_s, sen_mut.words[index_s])
  elif mut_type == 'del':
    if index_s < index_e:
      for i in range(len(sen_conllu.words)):
        if i < index_s or i > index_e:
          correct_words.append(sen_conllu.words[i])
  return correct_words

nlp = stanza.Pipeline('en', STANZA_MODEL_PATH, processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)

corpus = io.open('corpus/ud-treebanks-v2.7/UD_English-EWT/en_ewt-ud-train.conllu', "r", encoding="utf-8")
sen_words_list = []
progress_counter = Counter('Processing: ')
for sen in conllu.parse_incr(corpus):
  temp_words_list = []
  sen_conllu = PTF_Sen(sen, type='conllu')
  temp_words_list.append(sen_conllu.words)
  # add
  mut_sens_ids = sen_conllu.mutation_unmask_n_word()
  for mut_sen_id in mut_sens_ids:
    sen_mut = PTF_Sen(nlp(mut_sen_id[0]), type=NLP_TOOL, build_tree=False)
    if mut_deprel_type_compare_append_n_id(sen_conllu, sen_mut, mut_sen_id[1]):
      temp_words_list.append(get_mutant(sen_conllu, sen_mut, 'add'))
  # del
  mut_sen_del = sen_conllu.mutation_del_n_part()
  for sen_del in mut_sen_del:
    sen_mut = PTF_Sen(nlp(sen_del['sen']), type=NLP_TOOL, build_tree=False)
    temp_words_list.append(get_mutant(sen_conllu, sen_mut, 'del'))
  sen_words_list.append(temp_words_list)
  progress_counter.next()
progress_counter.finish()
print('writing')
max_mutants_num = 0
for sen in sen_words_list:
  if len(sen)>max_mutants_num:
    max_mutants_num = len(sen)
for sen in sen_words_list:
  for mut in sen:
    write_words(mut)
  for i in range(max_mutants_num-len(sen)):
    write_words(sen[0])