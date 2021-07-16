from queue import Queue
from itertools import combinations

NONSENSE_WORDS = ['Oh , ', 'Yup , ', 'Um , ', 'Ah , ', 'Indeed , ', 'In fact , ', 'Actually , ']
DEL_PART_PATTERN = (
  ('nmod', 'case'),
  ('x', 'advmod'),
  ('x', 'amod'),
  ('obl', 'case')
)

class SenMut:
  def __init__(self, stanza_words):
    self.words = stanza_words
    self.tree = self.build_tree()


  def mutation_clause_exchange(self):
    list_sens = []
    if 'children' not in self.tree:
      return list_sens
    for advcl in self.tree['children']:
      #clause is a advcl + SCONJ
      if advcl['deprel'] == 'advcl' and 'children' in advcl:
        for sconj in advcl['children']:
          if sconj['pos'] == 'SCONJ':
            clause_range = self.get_subtree_id_range(advcl)
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


  def get_subtree_id_range(self, tree):
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


  def mutation_add_comma(self):
    list_sens = []
    if 'children' not in self.tree:
      return []
    for obl in self.tree['children']:
      if obl['deprel'] == 'obl' and 'children' in obl:
        for case in obl['children']:
          if case['pos'] == 'ADP':
            clause_range = self.get_subtree_id_range(obl)
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


  def is_part_can_be_del(self, t, st):
    if (t['deprel'], st['deprel']) in DEL_PART_PATTERN:
      return True
    else:
      return False


  def mutation_del_part(self):
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
          if self.is_part_can_be_del(t, st):
            del_parts.append(self.get_subtree_id_range(t))
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

  
  def mutation_add_nonsense(self):
    list_sens = []
    sen = []
    for i in range(len(self.words)):
      sen.append(self.words[i].text.lower() if self.words[i].upos !=  'PROPN' and i == 0 else self.words[i].text)
    sen = ' '.join(sen)
    for nonsense in NONSENSE_WORDS:
      list_sens.append(nonsense + sen)
    return list_sens


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
                and_range1 = self.get_subtree_id_range(t)
                and_range2 = self.get_subtree_id_range(st)
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


  def build_tree(self):
    q_tree = Queue(maxsize=0)
    q_id = Queue(maxsize=0)
    root = {}
    for word in self.words:
      if word.head == 0:
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

  #build word:pos dict
  def to_compare(self):
    word_pos_dict = {}
    for word in self.words:
      word_pos_dict[word.text] = word.upos
    return word_pos_dict

  def to_doc(self):
    return ' '.join([word.text for word in self.words])


def mut_pos_compare_res(sen1, sen2):
  res = []
  dict1 = sen1.to_compare()
  dict2 = sen2.to_compare()
  for key in dict1.keys():
    if key in dict2:
      if dict1[key] != dict2[key]:
        res.append((key, dict1[key], dict2[key]))
  return res


def mut_pos_compare(sen1, sen2):
  dict1 = sen1.to_compare()
  dict2 = sen2.to_compare()
  for key in dict1.keys():
    if key in dict2:
      if dict1[key] != dict2[key]:
        return False
  return True