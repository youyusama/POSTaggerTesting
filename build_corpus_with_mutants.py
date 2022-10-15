import csv
import stanza
from config import *
import random
nlp = stanza.Pipeline('en', STANZA_MODEL_PATH, processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)

add_csv_filename = 'acl_results/annotated/modifier_mutation_EWT_stanza_ADD.CSV'
del_csv_filename = 'acl_results/annotated/modifier_mutation_EWT_stanza_DEL.CSV'

anno_sen_list = []

def to_doc(words):
  return ' '.join([word.text for word in words])

class Anno_Sen():
  def __init__(self, text):
    self.words = nlp(text).sentences[0].words
    self.muts = []
  
  def add_mutant(self, text, mut_type):
    mut_words = nlp(text).sentences[0].words
    index_s = 0
    index_e = len(mut_words)-1
    index_e_o = len(self.words)-1
    while self.words[index_s].text == mut_words[index_s].text:
      index_s += 1
    while self.words[index_e_o].text == mut_words[index_e].text:
      index_e -= 1
      index_e_o -= 1
    if mut_type == 'add':
      if index_s == index_e:
        correct_words = [word for word in self.words]
        correct_words.insert(index_s, mut_words[index_s])
        self.muts.append(correct_words)
    elif mut_type == 'del':
      if index_s < index_e:
        for i in range(len(self.words)):
          if i < index_s or i > index_e:
            correct_words.append(self.words[i])
        self.muts.append(correct_words)


with open(add_csv_filename, 'r', encoding='utf-8', errors='ignore') as csv_file:
  reader = csv.reader(csv_file)
  tp_flag = False
  for line in reader:
    if line[0] == 'original sentence':
      if tp_flag:
        anno_sen_list.append(temp_sen)
      temp_sen = Anno_Sen(line[1])
    if line[0] == 'wrong word':
      if line[2] == 'TP':
        tp_flag = True
      else:
        tp_flag = False
    if tp_flag and line[0] == 'mutation sentence':
      temp_sen.add_mutant(line[1], 'add')

with open(add_csv_filename, 'r', encoding='utf-8', errors='ignore') as csv_file:
  reader = csv.reader(csv_file)
  tp_flag = False
  for line in reader:
    if line[0] == 'original sentence':
      if tp_flag:
        anno_sen_list.append(temp_sen)
      temp_sen = Anno_Sen(line[1])
    if line[0] == 'wrong word':
      if line[2] == 'TP':
        tp_flag = True
      else:
        tp_flag = False
    if tp_flag and line[0] == 'mutation sentence':
      temp_sen.add_mutant(line[1], 'del')

f = open('mutant_corpus/mutant_corpus_one_quarter.conllu', mode='w+', encoding='utf-8')
sen_id = 1
for sen in anno_sen_list:
  if len(sen.muts) == 0:
    continue
  if random.random() < 0.75:
    continue
  mut = sen.muts[0]
  f.write('# sent_id = mut' + str(sen_id) + '\n')
  f.write('# text = ' + to_doc(mut) + '\n')
  w_id = 1
  for word in mut:
    f.write(str(w_id)+'\t' + word.text + '\t' + word.lemma +'\t' +word.upos + '\t' + word.xpos + '\t' + '_\t'+ str(word.head) + '\t'+ '_\t'+ '_\t'+ '_\n')
    w_id += 1
  sen_id += 1
  f.write('\n')
