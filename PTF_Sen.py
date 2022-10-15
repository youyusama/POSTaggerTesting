from queue import Queue
from itertools import combinations
from importlib_metadata import FastPath
from transformers import pipeline, set_seed
from PTF_Err import PTF_Err
from spacy.tokens import Doc
from config import *
import random
import math

random.seed(301)

def pcmp(x):
  return x[0]


unmasker = pipeline('fill-mask', model='xlm-roberta-base', top_k = UNMASK_NUM)
# generator = pipeline('text-generation', model='gpt2-large')

# to adapte the conllu struct to stanza-like words
class WordStanza:
  def __init__(self, word_inf):
    self.text = word_inf[0]
    self.upos = word_inf[1]
    self.head = word_inf[2]
    self.deprel = word_inf[3]
    self.id = word_inf[4]
    if len(word_inf)>5:
      self.xpos = word_inf[5]
    if len(word_inf)>6:
      self.lemma = word_inf[6]


# wish it's the final vision of the Class for sentence
# pos tag fuzzing sentence class
class PTF_Sen():

  __NONSENSE_WORDS = ['Oh , ', 'Yup , ', 'Um , ', 'Ah , ', 'Indeed , ', 'In fact , ', 'Actually , ']

  # *nolonger used*
  # patterns that seems can be deleted
  __DEL_PART_PATTERN = (
    ('nmod', 'case'),
    ('obl', 'case')
  )
  #words that seems can be deleted
  __DEL_WORD_PATTERN = ('advmod', 'amod')


  def __init__(self, temp, type='stanza', build_tree=True):#it's hard to maintain 'temp' as a fix type, so just temp
    if type == 'stanza':
      self.words = temp.sentences[0].words
    elif type == 'conllu':
      self.words = [WordStanza((word['form'], word['upos'], word['head'], word['deprel'], word['id'], word['xpos'], word['lemma'])) for word in temp if isinstance(word['id'], int)]
    elif type == 'spaCy':
      self.words = [WordStanza((word.text, word.pos_, word.head.i + 1, word.dep_, word.i + 1)) if word.head.i != word.i else WordStanza((word.text, word.pos_, 0, word.dep_, word.i + 1)) for word in temp]

    if build_tree:
      self.tree = self.__build_tree()



  # change the if,when clauses' position
  def mutation_clause_exchange(self):
    list_sens = []
    if 'children' not in self.tree:
      return list_sens
    for advcl in self.tree['children']:
      #clause is a advcl + SCONJ
      if advcl['deprel'] == 'advcl' and 'children' in advcl:
        for sconj in advcl['children']:
          if sconj['pos'] == 'SCONJ':
            clause_range = self.__get_subtree_id_range(advcl)
            #clause at begin
            if clause_range[0] == 1:
              sen = [word.text for word in self.words if word.id > clause_range[1]]
              if sen[0] == ',':
                del(sen[0])
              end_note = sen[-1]
              del(sen[-1])
              sen.append(',')
              sen += [word.text for word in self.words if word.id <= clause_range[1]]
              if sen[-1] == ',':
                del(sen[-1])
              sen.append(end_note)
              list_sens.append(' '.join(sen))
            #clause at last
            elif clause_range[1] == -1:
              sen = [word.text for word in self.words if word.id >= clause_range[0]]
              if sen[0] == ',':
                del(sen[0])
              del(sen[-1])
              sen.append(',')
              sen += [word.text for word in self.words if word.id < clause_range[0]]
              if sen[-1] == ',':
                del(sen[-1])
                sen.append('.')
              list_sens.append(' '.join(sen))
    return list_sens


	# add comma
  def mutation_add_comma(self):
    list_sens = []
    if 'children' not in self.tree:
      return []
    for obl in self.tree['children']:
      if obl['deprel'] == 'obl' and 'children' in obl:
        for case in obl['children']:
          if case['pos'] == 'ADP':
            clause_range = self.__get_subtree_id_range(obl)
            if clause_range[0] == 1:
              #already has comma
              if self.words[clause_range[1]].text == ',' or self.words[clause_range[1]-1].text == ',':
                return []
              #add comma
              sen = [word.text for word in self.words if word.id <= clause_range[1]]
              sen.append(',')
              sen += [word.text for word in self.words if word.id > clause_range[1]]
              list_sens.append(' '.join(sen))
              return list_sens
    return []


  def __is_word_can_be_del(self, st):
    if st['deprel'].endswith('mod') and st['deprel'] != 'nummod':
      return True
    else:
      return False

  def __is_part_can_be_del(self, t, st):
    if st['deprel'] == 'case' and ( t['deprel'].endswith('mod') or t['deprel'].startswith('obl') ):
      return True
    else:
      return False


  # bert insert word for unmask file
  def mutation_bert_insert_word_just_gen(self):
    list_unmask_info = []
    for i in range(len(self.words)-1):
      #add mask
      mask_id = i + 2
      masked_sen = ' '.join([word.text if word.id != i+1 else word.text + ' [MASK]' for word in self.words])
      #gen
      unmasked_sens = unmasker(masked_sen)
      for unmasked_sen in unmasked_sens:
        list_unmask_info.append((' '.join([word.text if word.id != i+1 else word.text + ' ' + unmasked_sen['token_str'] for word in self.words]), mask_id, unmasked_sen['token_str'], unmasked_sen['score']))
    return list_unmask_info


  # bert replace word for unmask file
  def mutation_bert_replace_word(self):
    list_unmask_info = []
    for i in range(len(self.words)):
      #add mask
      mask_id = i + 1
      masked_sen = ' '.join([word.text if word.id != i+1 else '[MASK]' for word in self.words])
      #gen
      unmasked_sens = unmasker(masked_sen)
      for unmasked_sen in unmasked_sens:
        list_unmask_info.append((' '.join([word.text if word.id != i+1 else unmasked_sen['token_str'] for word in self.words]), mask_id, unmasked_sen['token_str'], unmasked_sen['score']))
    return list_unmask_info


  def unmask_mut_filter(self, unmasks):
    list_sens_id = []
    for unmask in unmasks:
      if unmask['score'] >= 0.01 and self.__is_wanted_word(unmask['word'], unmask['id']):
        list_sens_id.append((unmask['sen'], [unmask['id']]))
    return list_sens_id
        


  # bert insert word
  def mutation_bert_insert_word(self):
    list_sens_id = []
    for i in range(len(self.words)-1):
      #add mask
      mask_id = i + 2
      masked_sen = ' '.join([word.text if word.id != i+1 else word.text + ' [MASK]' for word in self.words])
      #gen
      unmasked_sens = unmasker(masked_sen)
      for unmasked_sen in unmasked_sens:
        list_sens_id.append((' '.join([word.text if word.id != i+1 else word.text + ' ' + unmasked_sen['token_str'] for word in self.words]), mask_id))
    return list_sens_id


  # filter unwanted gen words
  def __is_wanted_word_n(self, gen_word, mask_id, words):
    if len(gen_word) < 4:
      return False
    if gen_word in self.__UNWANTED_WORDS:
      return False
    for punct in self.__UNWANTED_PUNCT:
      if punct in gen_word:
        return False
    # no repeat
    if mask_id-2>=0 and gen_word == words[mask_id-2]:
      return False
    return True


  # bert insert n word
  def mutation_unmask_n_word(self):
    rflag = 0
    if MUTATION_TIMES != -1:
      # rflag = math.pow(math.pow(0.1/MUTATION_TIMES, MUTATION_TIMES), 1/MUTATION_TIMES)
      rflag = 0.3
    to_unmasked_list_sens_id = []
    to_unmasked_list_sens_id.append(([word.text for word in self.words], []))
    list_sens_id = []
    for t in range(MUTATION_TIMES):
      for sen_id in to_unmasked_list_sens_id:
        for i in range(len(sen_id[0])-1):
          if random.random() >= rflag:
            continue
          #add mask
          mask_id = i + 2
          masked_sen = [word for word in sen_id[0]]
          masked_sen.insert(i+1 , '<mask>')
          masked_sen = ' '.join(masked_sen)
          #gen
          unmasked_sens = unmasker(masked_sen)
          for unmasked_sen in unmasked_sens:
            if unmasked_sen['score'] >= 0.01 and self.__is_wanted_word_n(unmasked_sen['token_str'], mask_id, sen_id[0]):
              temp_sen_id = ([word for word in sen_id[0]], [maskid for maskid in sen_id[1]])
              temp_sen_id[0].insert(i+1, unmasked_sen['token_str'])
              for j in range(len(temp_sen_id[1])):
                if temp_sen_id[1][j] >= mask_id:
                  temp_sen_id[1][j] += 1
              # for maskid in temp_sen_id[1]:
              #   if maskid >= mask_id:
              #     maskid += 1
              temp_sen_id[1].append(mask_id)
              list_sens_id.append(temp_sen_id)
      to_unmasked_list_sens_id = list_sens_id
      list_sens_id = []
      rflag *= 0.3
    for sen_id in to_unmasked_list_sens_id:
      list_sens_id.append((' '.join(sen_id[0]), sen_id[1]))
    # print(len(list_sens_id))
    return list_sens_id



  # bert insert word deprel persent
  def mutation_bert_insert_word_persent(self):
    list_sens_id = []
    for i in range(len(self.words)-1):
      #add mask
      mask_id = i + 2
      masked_sen = ' '.join([word.text if word.id != i+1 else word.text + ' [MASK]' for word in self.words])
      #gen
      unmasked_sens = unmasker(masked_sen)
      for unmasked_sen in unmasked_sens:
        # high score
        if unmasked_sen['score'] < 0.01:
          continue
        if self.__is_wanted_word(unmasked_sen['token_str'], mask_id):
          list_sens_id.append((' '.join([word.text if word.id != i+1 else word.text + ' ' + unmasked_sen['token_str'] for word in self.words]), mask_id))
    return list_sens_id


  __UNWANTED_WORDS = ['to', 'of', 'for', 'by', 'and', 'or', 'nor', 'a', 'an', 'the']
  __UNWANTED_PUNCT = ['#', '...', '-', ':', ',', ';', '"', "'"]
  # filter unwanted gen words
  def __is_wanted_word(self, gen_word, mask_id):
    if gen_word in self.__UNWANTED_WORDS:
      return False
    for punct in self.__UNWANTED_PUNCT:
      if punct in gen_word:
        return False
    # no repeat
    if mask_id-2>=0 and gen_word == self.words[mask_id-2].text:
      return False
    return True


  # mask around the proper words pos
  def __is_wanted_mask(self, mask_id):
    # front word [mask_id - 2]
    # back word [mask_id - 1]
    # before the 's 'll
    if self.words[mask_id-1].text.startswith("’") or self.words[mask_id-1].text.startswith("'"):
      return False
    # before the SCONJ
    if self.words[mask_id-1].upos == 'SCONJ':
      return False
    # not around ADP/PUNCT
    if self.words[mask_id-2].upos in ('ADP', 'PUNCT') or self.words[mask_id-1].upos in ('ADP', 'PUNCT'):
      return False
    return True


  # bert insert word filter error
  def mutation_bert_insert_word_filtered(self):
    list_sens_id = []
    for i in range(len(self.words)-1):
      mask_id = i + 2
      #around the proper words pos
      if not self.__is_wanted_mask(mask_id):
        continue
      #add mask
      masked_sen = ' '.join([word.text if word.id != i+1 else word.text + ' [MASK]' for word in self.words])
      #gen
      unmasked_sens = unmasker(masked_sen)
      for unmasked_sen in unmasked_sens:
        # high score
        if unmasked_sen['score'] < 0.01:
          continue
        if self.__is_wanted_word(unmasked_sen['token_str'], mask_id):
          list_sens_id.append((' '.join([word.text if word.id != i+1 else word.text + ' ' + unmasked_sen['token_str'] for word in self.words]), mask_id))
    return list_sens_id


  # mask around the proper pos around
  def __is_wanted_pos_around(self, mask_id):
    # front word [mask_id - 2]
    # back word [mask_id - 1]
    # around VERB/NOUN
    if self.words[mask_id-2].upos in ('VERB', 'NOUN') or self.words[mask_id-1].upos in ('VERB', 'NOUN'):
      return True
    # before ADJ/PRON
    if self.words[mask_id-1].upos in ('ADJ', 'PROP'):
      return True
    # end of the sentence
    if self.words[mask_id-1].upos == 'PUNCT' and self.words[mask_id-1].text == '.':
      return True
    return False


  # bert insert around words
  def mutation_bert_insert_around_words(self):
    list_sens_id = []
    for i in range(len(self.words)-1):
      #add mask
      mask_id = i + 2
      #around the proper words pos
      if not self.__is_wanted_pos_around(mask_id):
        continue
      masked_sen = ' '.join([word.text if word.id != i+1 else word.text + ' [MASK]' for word in self.words])
      #gen
      unmasked_sens = unmasker(masked_sen)
      for unmasked_sen in unmasked_sens:
        # high score
        if unmasked_sen['score'] < 0.01:
          continue
        if self.__is_wanted_word(unmasked_sen['token_str'], mask_id):
          list_sens_id.append((' '.join([word.text if word.id != i+1 else word.text + ' ' + unmasked_sen['token_str'] for word in self.words]), mask_id))
    return list_sens_id


  # mask and gen the redundant word
  def mutation_mask_and_gen_part(self):
    mask_ids = []
    list_sens_id = []
    #find parts can be del
    q = Queue(maxsize=0)
    q.put(self.tree)
    while not q.empty():
      t = q.get()
      if 'children' in t:
        for st in t['children']:
          q.put(st)
          if self.__is_part_can_be_del(t, st):
            mask_ids.append(t['id'])
      else:
        if self.__is_word_can_be_del(t):
          mask_ids.append(t['id'])
    #mask and gen
    origin_sen = self.to_doc()
    for mask_id in mask_ids:
      #mask word
      masked_sen = ' '.join([word.text if word.id != mask_id else '[MASK]' for word in self.words])
      #gen
      unmasked_sens = unmasker(masked_sen)
      for unmasked_sen in unmasked_sens:
        if unmasked_sen['token_str'] != self.words[mask_id-1]:
          list_sens_id.append((' '.join([word.text if word.id != mask_id else unmasked_sen['token_str'] for word in self.words]), mask_id))
    return list_sens_id


  # del the redundant part 1
  def mutation_del_part(self):
    list_sen_del = []
    del_parts = []
    #find parts can be del
    q = Queue(maxsize=0)
    q.put(self.tree)
    while not q.empty():
      t = q.get()
      if 'children' in t:
        for st in t['children']:
          q.put(st)
          if self.__is_part_can_be_del(t, st):
            del_parts.append(self.__get_subtree_id_range(t))
      else:
        if self.__is_word_can_be_del(t):
          del_parts.append(self.__get_subtree_id_range(t))
    #del mutation 1 part
    for del_part in del_parts:
      # VERB-ADP
      if self.words[del_part[0]-2].upos == 'VERB' and self.words[del_part[0]-1].upos == 'ADP':
        continue

      sen = [word.text for word in self.words]
      for i in range(del_part[0]-1, del_part[1]):
        sen[i] = ''
      sen_del = {'sen':' '.join([word for word in sen if word != '']), 'del': del_part}
      list_sen_del.append(sen_del)
    return list_sen_del


  # del the redundant part n
  def mutation_del_n_part(self):
    list_sen_del = []
    del_parts = []
    #find parts can be del
    q = Queue(maxsize=0)
    q.put(self.tree)
    while not q.empty():
      t = q.get()
      if 'children' in t:
        for st in t['children']:
          q.put(st)
          if self.__is_part_can_be_del(t, st):
            del_parts.append(self.__get_subtree_id_range(t))
      else:
        if self.__is_word_can_be_del(t):
          del_parts.append(self.__get_subtree_id_range(t))
    #clean mutation parts

    del_parts.sort(key = lambda x:(x[0],x[1]))
    len_del = len(del_parts)
    i = 0
    while i < len_del-1:
      if del_parts[i][1] >= del_parts[i+1][0]:
        del del_parts[i]
        i -= 1
        len_del -= 1
      i += 1

    #del mutation n part
    if len(del_parts) < MUTATION_TIMES:
      return []
    else:
      for com_del_parts in combinations(del_parts, MUTATION_TIMES):
        # VERB-ADP
        fflag = False
        for del_part in com_del_parts:
          if self.words[del_part[0]-2].upos == 'VERB' and self.words[del_part[0]-1].upos == 'ADP':
            fflag = True
            break
        if fflag:
          continue

        sen = [word.text for word in self.words]
        for del_part in com_del_parts:
          for j in range(del_part[0]-1, del_part[1]):
            sen[j] = ''
        if sen[0] == ',':
          del(sen[0])

        sen_del = {'sen':' '.join([word for word in sen if word != '']), 'del': com_del_parts}
        list_sen_del.append(sen_del)
    # print(list_sen_del)
    return list_sen_del


	# del the redundant part combination
  def mutation_del_part_combination(self):
    list_sens = []
    del_parts = []
    #find parts can be del
    q = Queue(maxsize=0)
    q.put(self.tree)
    while not q.empty():
      t = q.get()
      if 'children' in t:
        for st in t['children']:
          q.put(st)
          if self.__is_part_can_be_del(t, st):
            del_parts.append(self.__get_subtree_id_range(t))
      else:
        if self.__is_word_can_be_del(t):
          del_parts.append(self.__get_subtree_id_range(t))
    #del mutation combinations
    for i in range(1, len(del_parts)+1):
      for com_del_parts in combinations(del_parts, i):
        sen = [word.text for word in self.words]
        for del_part in com_del_parts:
          for j in range(del_part[0]-1, del_part[1]):
            sen[j] = ''
        if sen[0] == ',':
          del(sen[0])
        list_sens.append(' '.join([word for word in sen if word != '']))
    return list(set(list_sens))


  # add next sentence
  def mutation_add_next_sen(self):
    gens = generator(self.to_doc(), num_return_sequences=10, pad_token_id=50256)
    return [gen['generated_text'] for gen in gens]

  
	# add nonsense words at begining
  def mutation_add_nonsense(self):
    list_sens = []
    sen = []
    for i in range(len(self.words)):
      sen.append(self.words[i].text.lower() if self.words[i].upos !=  'PROPN' and i == 0 else self.words[i].text)
    sen = ' '.join(sen)
    for nonsense in self.__NONSENSE_WORDS:
      list_sens.append(nonsense + sen)
    return list_sens


	# exchange the words beside and,or
  def mutation_exchange_and(self):
    list_sens = []
    and_couples = []
    #find and couples
    q = Queue(maxsize=0)
    q.put(self.tree)
    while not q.empty():
      t = q.get()
      if 'children' in t:
        for st in t['children']:
          q.put(st)
          if st['deprel'] == 'conj' and t['deprel'] == 'obj' and 'children' in st:
            for cconj in st['children']:
              if cconj['deprel'] == 'cc' and cconj['pos'] == 'CCONJ':
                and_range1 = self.__get_subtree_id_range(t)
                and_range2 = self.__get_subtree_id_range(st)
                if and_range1[1] == and_range2[1] and and_range1[0] < and_range2[0]:
                  and_couples.append([and_range1, and_range2])
    #and couples mutation
    for and_couple in and_couples:
      sen = [word.text for word in self.words if word.id < and_couple[0][0]]
      sen += [word.text for word in self.words if (word.id > and_couple[1][0] and word.id <= and_couple[1][1])]
      sen.append(self.words[and_couple[1][0]-1].text)
      sen += [word.text for word in self.words if (word.id >= and_couple[0][0] and word.id < and_couple[1][0])]
      sen += [word.text for word in self.words if word.id > and_couple[0][1]]
      list_sens.append(' '.join(sen))
    return list_sens


  #build word:pos dict for compare
  def dict_for_compare(self):
    word_pos_dict = {}
    for word in self.words:
      word_pos_dict[word.text] = word.upos
    return word_pos_dict


  def show_for_test(self):
    for word in self.words:
      print(word.id, word.text, word.upos, word.deprel, word.head)


  def to_doc(self):
    return ' '.join([word.text for word in self.words])


  def __get_subtree_id_range(self, tree):
    clause_range = [2000,-1]
    q = Queue(maxsize=0)
    q.put(tree)
    while not q.empty():
      t = q.get()
      if t['id'] < clause_range[0]:
        clause_range[0] = t['id']
      if t['id'] > clause_range[1]:
        clause_range[1] = t['id']
      if 'children' in t:
        for st in t['children']:
          q.put(st)
    return clause_range


  def __build_tree(self):
    q_tree = Queue(maxsize=0)
    q_id = Queue(maxsize=0)
    root = {}
    for word in self.words:
      if word.head == 0 or word.head == word.id:
        word.head = 0
        root = {'text': word.text, 'pos': word.upos, 'deprel': word.deprel, 'id': word.id}
    q_tree.put(root)
    q_id.put(root['id'])
    while not q_id.empty():
      tree = q_tree.get()
      id = q_id.get()
      for word in self.words:
        if word.head == id:
          subtree = {'text': word.text, 'pos': word.upos, 'deprel': word.deprel, 'id': word.id}
          if 'children' not in tree:
            tree['children'] = []
          tree['children'].append(subtree)
          q_tree.put(subtree)
          q_id.put(subtree['id'])
    return root


class WhitespaceTokenizer:
  def __init__(self, vocab):
    self.vocab = vocab

  def __call__(self, text):
    words = text.split(" ")
    spaces = [True] * len(words)
    # Avoid zero-length tokens
    for i, word in enumerate(words):
      if word == "":
        words[i] = " "
        spaces[i] = False
    # Remove the final trailing space
    if words[-1] == " ":
      words = words[0:-1]
      spaces = spaces[0:-1]
    else:
      spaces[-1] = False
    return Doc(self.vocab, words=words, spaces=spaces)
