from PTF_Sen import *
from compare_utilities import *
import conllu
import io
import stanza
import spacy
from global_variables import *
from spacy.tokens import Doc
from config import *
from bert_sens_gen import bert_gen_or_read
from unmask_file_reader import *

#create error_map
tag_list_U = ('ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X')
error_map_sen= {}
for key in tag_list_U:
  error_map_sen[key]={}
  for key2 in tag_list_U:
    error_map_sen[key][key2]=0

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

if __name__ == '__main__':
  #load corpus
  corpus = io.open(CORPUS_PATH, "r", encoding="utf-8")
  #load nlp tools
  nlp_stanza = stanza.Pipeline('en', STANZA_MODEL_PATH, processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
  nlp_spaCy = spacy.load(SPACY_MODEL_NAME, exclude=['lemmatizer', 'ner'])
  nlp_spaCy.tokenizer = WhitespaceTokenizer(nlp_spaCy.vocab)

  sen_num = 0
  mut_sen_num = 0
  token_num = 0
  stanza_wrong_token = 0
  spaCy_wrong_token = 0
  stanza_wrong_sen_num = 0
  spaCy_wrong_sen_num = 0

  for sen in conllu.parse_incr(corpus):
    print(sen_num)
    sen_num += 1
    # sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
    # if len(sen_conllu.words)<=5:
    #   continue
    
    # sen_stanza = PTF_Sen(nlp_stanza(sen_conllu.to_doc()), type='stanza', build_tree=False)
    # sen_spaCy = PTF_Sen(nlp_spaCy(sen_conllu.to_doc()), type='spaCy', build_tree=False)

    # token_num += len(sen_conllu.words)
    # if simple_compare_pos(sen_conllu, sen_stanza):
    #   stanza_wrong_sen_num += 1
    # if simple_compare_pos(sen_conllu, sen_spaCy):
    #   spaCy_wrong_sen_num += 1

    # sen_length = len(sen_conllu.words)
    # for i in range(sen_length):
    #   if sen_conllu.words[i].upos != sen_spaCy.words[i].upos:
    #     error_map_sen[sen_conllu.words[i].upos][sen_spaCy.words[i].upos] += 1


  # #sen map
  # print("process y as x:")
  # print('-\\-',end='')
  # for key in error_map_sen.keys():
  #   print('\t'+str(key),end=' ')
  # print('')
  # for key in error_map_sen.keys():
  #   print(str(key), end='\t')
  #   for key2 in error_map_sen[key].keys():
  #     print(str(error_map_sen[key][key2]), end='\t')
  #   print('')


  # # generate the unmasked sentences file
  # gen_filename = bert_gen_or_read(CORPUS_PATH)
  # # iterate reader
  # reader = Unmask_File_Reader(gen_filename)

  # for sen in conllu.parse_incr(corpus):
  #   sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
  #   # short sen unwanted
  #   if len(sen_conllu.words) <= 5:
  #     if MUTATION_WAY == 'ADD':
  #       reader_skip_sen(reader, sen_conllu)
  #     continue

  #   mut_sens_ids = sen_conllu.unmask_mut_filter(reader_mut(reader, sen_conllu))
  #   for mut_sen_id in mut_sens_ids:
  #     mut_stanza = PTF_Sen(nlp_stanza(mut_sen_id[0]), type='stanza', build_tree=False)
  #     mut_spaCy = PTF_Sen(nlp_spaCy(mut_sen_id[0]), type='spaCy', build_tree=False)
  #     token_num += len(sen_conllu.words)
  #     mut_sen_num += 1
  #     res = mut_pos_compare_appendid_res(sen_conllu, mut_stanza, mut_sen_id[1])
  #     if len(res) > 0:
  #       stanza_wrong_token += len(res)
  #       stanza_wrong_sen_num += 1
  #     res = mut_pos_compare_appendid_res(sen_conllu, mut_spaCy, mut_sen_id[1])
  #     if len(res) > 0:
  #       spaCy_wrong_token += len(res)
  #       spaCy_wrong_sen_num += 1
    
  print(sen_num)
  print(mut_sen_num)
  print(token_num)
  print(stanza_wrong_token)
  print(spaCy_wrong_token)
  print(stanza_wrong_sen_num)
  print(spaCy_wrong_sen_num)

  # 490576
  # 13942003
  # 345292
  # 845889
  # 221744
  # 357033