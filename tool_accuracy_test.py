from PTF_Sen import *
from compare_utilities import *
import conllu
import io
import stanza
import spacy
from global_variables import *
from spacy.tokens import Doc

CORPUS_PATH = '/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu'

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
  nlp_stanza = stanza.Pipeline('en', NLP_MODEL_PATH + 'stanzamodel/stanza_model/', processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
  nlp_spaCy = spacy.load('en_core_web_trf', exclude=['lemmatizer', 'ner'])
  nlp_spaCy.tokenizer = WhitespaceTokenizer(nlp_spaCy.vocab)

  sen_num = 0
  # stanza_right = 0
  # spaCy_right = 0
  # token_num = 0
  # stanza_wrong_token = 0
  # spaCy_wrong_token = 0
  stanza_dep_list = set()
  spaCy_dep_list = set()

  for sen in conllu.parse_incr(corpus):
    sen_num += 1
    print(sen_num)
    sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
    sen_stanza = PTF_Sen(nlp_stanza(sen_conllu.to_doc()), type='stanza', build_tree=False)
    sen_spaCy = PTF_Sen(nlp_spaCy(sen_conllu.to_doc()), type='spaCy', build_tree=False)
    for word in sen_stanza.words:
      stanza_dep_list.add(word.deprel)
    for word in sen_spaCy.words:
      spaCy_dep_list.add(word.deprel)

    # token_num += len(sen_conllu.words)
    # if simple_compare_pos(sen_conllu, sen_stanza):
    #   stanza_right += 1
    # if simple_compare_pos(sen_conllu, sen_spaCy):
    #   spaCy_right += 1
    # stanza_wrong_token += simple_compare_pos_count(sen_conllu, sen_stanza)
    # spaCy_wrong_token += simple_compare_pos_count(sen_conllu, sen_spaCy)
  print(stanza_dep_list)
  print(spaCy_dep_list)
  # print(sen_num, stanza_right, spaCy_right)
  # print(stanza_right/sen_num)
  # print(spaCy_right/sen_num)
  # print((token_num-stanza_wrong_token)/token_num)
  # print((token_num-spaCy_wrong_token)/token_num)
