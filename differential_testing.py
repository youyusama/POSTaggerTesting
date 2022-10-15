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
  # #load corpus
  # corpus = io.open('/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu', "r", encoding="utf-8")
  #load nlp tools
  nlp_stanza = stanza.Pipeline('en', STANZA_MODEL_PATH, processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
  nlp_spaCy = spacy.load(SPACY_MODEL_NAME, exclude=['lemmatizer', 'ner'])
  nlp_spaCy.tokenizer = WhitespaceTokenizer(nlp_spaCy.vocab)

  sen_num = 0
  token_num = 0
  t1_eq_t2 = 0
  t1_eq_t2_eq_c = 0
  t1_neq_t2 = 0
  t1_neq_t2_eq_c = 0
  t2_neq_t1_eq_c = 0
  t1_neq_t2_neq_c = 0  

  corpus_list = ['corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu',
  'corpus/ud-treebanks-v2.7/UD_English-EWT/en_ewt-ud-train.conllu',
  'corpus/ud-treebanks-v2.7/UD_English-Pronouns/en_pronouns-ud-test.conllu',
  'corpus/ud-treebanks-v2.7/UD_English-PUD/en_pud-ud-test.conllu']


  for corpus_path in corpus_list:
    #load corpus
    corpus = io.open(corpus_path, "r", encoding="utf-8")

    sen_num = 0
    token_num = 0
    t1_eq_t2 = 0
    t1_eq_t2_eq_c = 0
    t1_neq_t2 = 0
    t1_neq_t2_eq_c = 0
    t2_neq_t1_eq_c = 0
    t1_neq_t2_neq_c = 0 

    diff_res = io.open('statistics/'+corpus_path.split('.')[-2].split('/')[-1], 'w+', encoding='utf-8')

    for sen in conllu.parse_incr(corpus):
      sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
      if len(sen_conllu.words)<=5:
        continue

      sen_stanza = PTF_Sen(nlp_stanza(sen_conllu.to_doc()), type='stanza', build_tree=False)
      sen_spaCy = PTF_Sen(nlp_spaCy(sen_conllu.to_doc()), type='spaCy', build_tree=False)

      sen_length = len(sen_conllu.words)
      token_num += sen_length
      for i in range(sen_length):
        if sen_stanza.words[i].upos != sen_spaCy.words[i].upos:
          t1_neq_t2 += 1
          if sen_stanza.words[i].upos == sen_conllu.words[i].upos:
            t2_neq_t1_eq_c += 1
          if sen_spaCy.words[i].upos == sen_conllu.words[i].upos:
            t1_neq_t2_eq_c += 1
          if sen_stanza.words[i].upos != sen_conllu.words[i].upos and sen_spaCy.words[i].upos != sen_conllu.words[i].upos:
            t1_neq_t2_neq_c += 1
            diff_res.write('\nsentence:\n')
            diff_res.write(sen_conllu.to_doc() + '\n')
            diff_res.write('wrong word id: ' + str(i) + ' ' + sen_conllu.words[i].text + '\n')
            diff_res.write('corpus tag: ' + sen_conllu.words[i].upos + '\n')
            diff_res.write('stanza tag: ' + sen_stanza.words[i].upos + '\n')
            diff_res.write('spaCy tag: ' + sen_spaCy.words[i].upos + '\n')
        else:
          t1_eq_t2 += 1
          if sen_stanza.words[i].upos == sen_conllu.words[i].upos:
            t1_eq_t2_eq_c += 1

    diff_res.close()
    print(corpus_path)
    print(sen_num)
    print(token_num)
    print(t1_eq_t2)
    print(t1_eq_t2_eq_c)
    print(t1_neq_t2)
    print(t1_neq_t2_eq_c)
    print(t2_neq_t1_eq_c)
    print(t1_neq_t2_neq_c)