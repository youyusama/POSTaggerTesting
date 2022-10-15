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
from progress.counter import Counter
import csv

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

f_comp_and_not_diff = io.open('testing_methods_eva/comp_and_not_diff.csv', "w", encoding="utf-8")
csv_comp_and_not_diff = csv.writer(f_comp_and_not_diff)

f_comp_and_mm = io.open('testing_methods_eva/comp_and_mm.csv', "w", encoding="utf-8")
csv_comp_and_mm = csv.writer(f_comp_and_mm)

f_comp_and_not_mm = io.open('testing_methods_eva/comp_and_not_mm.csv', "w", encoding="utf-8")
csv_comp_and_not_mm = csv.writer(f_comp_and_not_mm)

f_not_comp_and_mm = io.open('testing_methods_eva/not_comp_and_mm.csv', "w", encoding="utf-8")
csv_not_comp_and_mm = csv.writer(f_not_comp_and_mm)

if __name__ == '__main__':
  #load nlp tools
  nlp_stanza = stanza.Pipeline('en', STANZA_MODEL_PATH, processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
  nlp_spaCy = spacy.load(SPACY_MODEL_NAME, exclude=['lemmatizer', 'ner'])
  nlp_spaCy.tokenizer = WhitespaceTokenizer(nlp_spaCy.vocab)

  # corpus_list = ['corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu',
  # 'corpus/ud-treebanks-v2.7/UD_English-EWT/en_ewt-ud-train.conllu',
  # 'corpus/ud-treebanks-v2.7/UD_English-Pronouns/en_pronouns-ud-test.conllu',
  # 'corpus/ud-treebanks-v2.7/UD_English-PUD/en_pud-ud-test.conllu']

  corpus_list = ['corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu']


  for corpus_path in corpus_list:
    #load corpus
    corpus = io.open(corpus_path, "r", encoding="utf-8")

    sen_num = 0
    token_num = 0
    diff_num = 0
    mm_num = 0
    diff_mm_num = 0
    comp_num = 0
    comp_diff_num = 0
    comp_mm_num = 0

    # generate the unmasked sentences file
    gen_filename = bert_gen_or_read(corpus_path)
    # iterate reader
    reader = Unmask_File_Reader(gen_filename)

    print(corpus_path)
    progress_counter = Counter('Processing: ')
    
    # for every sentence in corpus
    for sen in conllu.parse_incr(corpus):
      sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
      # short sen unwanted
      if len(sen_conllu.words) <= 5:
        reader_skip_sen(reader, sen_conllu)
        continue
      sen_num +=1
      token_num += len(sen_conllu.words)
      sen_nlp_stanza = PTF_Sen(nlp_stanza(sen_conllu.to_doc()), type='stanza')
      sen_nlp_spaCy = PTF_Sen(nlp_spaCy(sen_conllu.to_doc()), type='spaCy')

      progress_counter.next()

      # differential testing
      diff = set()
      for i in range(len(sen_conllu.words)):
        if sen_nlp_stanza.words[i].upos != sen_nlp_spaCy.words[i].upos:
          diff.add(i)

      # just comparing to the corpus
      comp = set()
      for i in range(len(sen_conllu.words)):
        if sen_conllu.words[i].upos != sen_nlp_spaCy.words[i].upos:
          comp.add(i)

      for i in range(len(sen_conllu.words)):
        if sen_conllu.words[i].upos != sen_nlp_stanza.words[i].upos:
          comp.add(i)
      comp_num += len(comp)

      # comp & !diff
      for i in comp:
        if i not in diff:
          csv_comp_and_not_diff.writerow(['wrong sentence:', sen_conllu.to_doc()])
          csv_comp_and_not_diff.writerow(['wrong word:' , sen_conllu.words[i].text ])
          csv_comp_and_not_diff.writerow(['wrong pos from * to stanza spaCy:', sen_conllu.words[i].upos ,sen_nlp_stanza.words[i].upos , sen_nlp_spaCy.words[i].upos])
          csv_comp_and_not_diff.writerow([])

      # multi mutation
      muts_add = []
      muts_del = []
      wt_set = set()
      wt_set_printed = set()
      # get mutation sentences
      mut_sens_ids = sen_conllu.unmask_mut_filter(reader_mut(reader, sen_conllu))
      for mut_sen_id in mut_sens_ids:
        sen_mut = PTF_Sen(nlp_stanza(mut_sen_id[0]), type='stanza', build_tree=False)
        # dependency filter
        if mut_deprel_type_compare_appendid(sen_nlp_stanza, sen_mut, mut_sen_id[1]):
          muts_add.append((sen_mut, mut_sen_id[1]))
      for mut in muts_add:
        wt_temp = mut_pos_compare_appendid_set(sen_nlp_stanza, mut[0], mut[1]) # count the token tagging error in mutants
        # accumulate error
        for i in wt_temp:
          if i in wt_set_printed:
            continue
          if i in comp:
            wt_set_printed.add(i)
            csv_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_comp_and_mm.writerow(['wrong word:', sen_conllu.words[i].text ])
            csv_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:', sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos, sen_nlp_spaCy.words[i].upos ])
            csv_comp_and_mm.writerow(['mutant', mut[0].to_doc() ])
            csv_comp_and_mm.writerow(['pos as', mut[0].words[i if i<mut[1]-1 else i+1].upos ])
            csv_comp_and_mm.writerow([])
          elif i not in comp:
            wt_set_printed.add(i)
            csv_not_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_not_comp_and_mm.writerow(['wrong word:' ,sen_conllu.words[i].text ])
            csv_not_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:' , sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos ,sen_nlp_spaCy.words[i].upos ])
            csv_not_comp_and_mm.writerow(['mutant' , mut[0].to_doc() ])
            csv_not_comp_and_mm.writerow(['pos as' , mut[0].words[i if i<mut[1]-1 else i+1].upos ])
            csv_not_comp_and_mm.writerow([])
        wt_set.update(wt_temp)
      muts_add = []
      
      for mut_sen_id in mut_sens_ids:
        sen_mut = PTF_Sen(nlp_spaCy(mut_sen_id[0]), type='spaCy', build_tree=False)
        # dependency filter
        if mut_deprel_type_compare_appendid(sen_nlp_spaCy, sen_mut, mut_sen_id[1]):
          muts_add.append((sen_mut, mut_sen_id[1]))
      for mut in muts_add:
        wt_temp = mut_pos_compare_appendid_set(sen_nlp_spaCy, mut[0], mut[1]) # count the token tagging error in mutants
        # accumulate error
        for i in wt_temp:
          if i in wt_set_printed:
            continue
          if i in comp:
            wt_set_printed.add(i)
            csv_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_comp_and_mm.writerow(['wrong word:', sen_conllu.words[i].text ])
            csv_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:', sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos, sen_nlp_spaCy.words[i].upos ])
            csv_comp_and_mm.writerow(['mutant', mut[0].to_doc() ])
            csv_comp_and_mm.writerow(['pos as', mut[0].words[i if i<mut[1]-1 else i+1].upos ])
            csv_comp_and_mm.writerow([])
          elif i not in comp:
            wt_set_printed.add(i)
            csv_not_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_not_comp_and_mm.writerow(['wrong word:' ,sen_conllu.words[i].text ])
            csv_not_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:' , sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos ,sen_nlp_spaCy.words[i].upos ])
            csv_not_comp_and_mm.writerow(['mutant' , mut[0].to_doc() ])
            csv_not_comp_and_mm.writerow(['pos as' , mut[0].words[i if i<mut[1]-1 else i+1].upos ])
            csv_not_comp_and_mm.writerow([])
        wt_set.update(wt_temp)

      # MUTATION_WAY =='DEL':
      # mutation sens check del
      mut_sen_del = sen_nlp_stanza.mutation_del_part()
      for sen_del in mut_sen_del:
        sen_mut = PTF_Sen(nlp_stanza(sen_del['sen']), type='stanza', build_tree=False)
        muts_del.append((sen_mut, sen_del['del']))
      for mut in muts_del:
        wt_temp = del_mut_pos_compare_set(sen_nlp_stanza, mut[0], mut[1]) # count the token tagging error in mutants
        # accumulate error
        for i in wt_temp:
          if i in wt_set_printed:
            continue
          if i in comp:
            wt_set_printed.add(i)
            csv_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_comp_and_mm.writerow(['wrong word:', sen_conllu.words[i].text ])
            csv_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:', sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos, sen_nlp_spaCy.words[i].upos ])
            csv_comp_and_mm.writerow(['mutant', mut[0].to_doc() ])
            csv_comp_and_mm.writerow([])
          elif i not in comp:
            wt_set_printed.add(i)
            csv_not_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_not_comp_and_mm.writerow(['wrong word:' ,sen_conllu.words[i].text ])
            csv_not_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:' , sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos ,sen_nlp_spaCy.words[i].upos ])
            csv_not_comp_and_mm.writerow(['mutant' , mut[0].to_doc() ])
            csv_not_comp_and_mm.writerow([])
        wt_set.update(wt_temp)
      muts_del = []

      for sen_del in mut_sen_del:
        sen_mut = PTF_Sen(nlp_spaCy(sen_del['sen']), type='spaCy', build_tree=False)
        muts_del.append((sen_mut, sen_del['del']))
      for mut in muts_del:
        wt_temp = del_mut_pos_compare_set(sen_nlp_spaCy, mut[0], mut[1]) # count the token tagging error in mutants
        # accumulate error
        for i in wt_temp:
          if i in wt_set_printed:
            continue
          if i in comp:
            wt_set_printed.add(i)
            csv_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_comp_and_mm.writerow(['wrong word:', sen_conllu.words[i].text ])
            csv_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:', sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos, sen_nlp_spaCy.words[i].upos ])
            csv_comp_and_mm.writerow(['mutant', mut[0].to_doc() ])
            csv_comp_and_mm.writerow([])
          elif i not in comp:
            wt_set_printed.add(i)
            csv_not_comp_and_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
            csv_not_comp_and_mm.writerow(['wrong word:' ,sen_conllu.words[i].text ])
            csv_not_comp_and_mm.writerow(['wrong pos from * to stanza spaCy:' , sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos ,sen_nlp_spaCy.words[i].upos ])
            csv_not_comp_and_mm.writerow(['mutant' , mut[0].to_doc() ])
            csv_not_comp_and_mm.writerow([])
        wt_set.update(wt_temp)
      

      mm_num += len(wt_set)

      
      for i in comp:
        if i not in wt_set:
          csv_comp_and_not_mm.writerow(['wrong sentence:', sen_conllu.to_doc() ])
          csv_comp_and_not_mm.writerow(['wrong word:' ,sen_conllu.words[i].text ])
          csv_comp_and_not_mm.writerow(['wrong pos from * to stanza spaCy:' , sen_conllu.words[i].upos , sen_nlp_stanza.words[i].upos ,sen_nlp_spaCy.words[i].upos ])
          csv_comp_and_not_mm.writerow([])

      for err in comp:
        if err in wt_set:
          comp_mm_num += 1
      
      diff_num += len(diff)
      for err in diff:
        if err in wt_set:
          diff_mm_num += 1
        if err in comp:
          comp_diff_num += 1
      
      

      # comp & mm (> diff & mm)

      # !comp & mm

      # comp & !mm


    progress_counter.finish()

    print(sen_num)
    print(token_num)
    print(comp_num)
    print(diff_num)
    print(mm_num)
    print(diff_mm_num)
    print(comp_diff_num)
    print(comp_mm_num)