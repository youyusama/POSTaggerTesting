import random
import io
random.seed(123)
# w2v_file = '/mnt/hd0/POStaggingFuzzing/nlp-models/glove/glove.6B.100d.w2v.txt'
# from gensim.models import KeyedVectors
# glove_model = KeyedVectors.load_word2vec_format(w2v_file, binary=False)
# #noun set
# noun_set_file = io.open('/mnt/hd0/POStaggingFuzzing/gen_data/noun_set.txt', 'r', encoding='utf-8')
# noun_set = {line.strip() for line in noun_set_file.readlines()}
# noun_set_in_w2v = [noun for noun in noun_set if noun in glove_model.vocab]

class WordStanza:
  def __init__(self, word_inf):
    self.text = word_inf[0]
    self.upos = word_inf[1]
    self.head = word_inf[2]
    self.deprel = word_inf[3]
    self.id = word_inf[4]


class SenOri:
  def __init__(self, sen_struct, sen_type):
    if sen_type == 'conllu':
      self.sen = [[word['form'], word['upos']] for word in sen_struct]
      self.ori = [(word['form'], word['upos'], word['head'], word['deprel'], word['id']) for word in sen_struct]
    elif sen_type == 'stanza':
      self.sen = [[word.text, word.upos] for word in sen_struct.words]
      self.ori = [(word.text, word.upos, word.head, word.deprel, word.id) for word in sen_struct.words]

  def to_doc(self):
    return str(' '.join(word[0] for word in self.sen))

  def to_stanza_words(self):
    return [WordStanza(word) for word in self.ori]

  #noun exchange
  def mutation_simple(self, noun_set, num=10):
    res = ''
    for i in range(len(self.sen)):
      if self.sen[i][1] == 'NOUN':
        for j in range(num):
          res += ' '.join([(noun_set[random.randint(0, len(noun_set_num)-1)] if k == i else self.sen[k][0]) for k in range(len(self.sen))]) + ' \n'
    return res

  #noun exchange by w2v meaning
  def mutation_noun_w2v(self, num=10):
    res = ''
    noun_i = []
    for i in range(len(self.sen)):
      if self.sen[i][1] == 'NOUN' and self.sen[i][0] in glove_model.vocab:
        noun_i.append(i)
        temp_noun_set = noun_set_in_w2v.copy()
        word_similar_list = []
        for j in range(num):
          word = glove_model.most_similar_to_given(self.sen[i][0], temp_noun_set)
          word_similar_list.append(word)
          temp_noun_set.remove(word)
        for j in range(len(word_similar_list)):
          res += ' '.join([ (word_similar_list[j] if k == i else self.sen[k][0] ) for k in range(len(self.sen))]) + '\n'
    return res, noun_i

           

def sen_pos_compare(sen1, sen2):
  res = []
  for i in range(len(sen1.sen)):
    if sen1.sen[i][1] != sen2.sen[i][1]:
      res.append((i, sen1.sen[i][1], sen2.sen[i][1]))
  return res

def is_pos_same(sen1, sen2):
  if len(sen_pos_compare(sen1, sen2)) == 0:
    return True
  else:
    return False

def is_pos_dep_same(sen1, sen2):
  for i in range(len(sen1.ori)):
    if sen1.ori[i][1] != sen1.ori[i][1] or sen1.ori[i][2] != sen2.ori[i][2]:
      return False
  return True

def is_dep_same(sen1, sen2):
  for i in range(len(sen1.ori)):
    if sen1.ori[i][2] != sen2.ori[i][2]:
      return False
  return True