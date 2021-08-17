from PTF_Sen import *
from PTF_Err import *
import conllu
import io
import time
import stanza
from bert_sens_gen import bert_gen_or_read
from unmask_file_reader import *
from map2csv import *
from compare_utilities import *
from global_variables import *
import spacy
from progress.counter import Counter
from config import *

error_map_tag_000= {}
error_map_tag_100= {}
error_map_tag_001= {}
error_map_tag_010= {}
create_error_map(error_map_tag_000)
create_error_map(error_map_tag_100)
create_error_map(error_map_tag_001)
create_error_map(error_map_tag_010)

if __name__ == '__main__':
  #load corpus
  corpus = io.open(CORPUS_PATH, "r", encoding="utf-8")
  #load nlp tools
  if NLP_TOOL == 'stanza':
    nlp = stanza.Pipeline('en', STANZA_MODEL_PATH, processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
  elif NLP_TOOL == 'spaCy':
    nlp = spacy.load(SPACY_MODEL_NAME, exclude=['lemmatizer', 'ner'])
    nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)

  if MUTATION_WAY == 'ADD':
    # generate the unmasked sentences file
    gen_filename = bert_gen_or_read(CORPUS_PATH)
    # iterate reader
    reader = Unmask_File_Reader(gen_filename)

  # statistic infos
  all_test_sen_num = 0
  c_n_same_sen_num = 0
  filtered_mut_num = 0
  #c-corpus - n-nlp - m-mutation -
  cnm_100_num = 0
  cnm_000_num = 0
  cnm_001_num = 0
  cnm_010_num = 0

  progress_counter = Counter('Processing: ')

  # for every sentence in corpus
  for sen in conllu.parse_incr(corpus):
    sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
    # short sen unwanted
    if len(sen_conllu.words) <= 5:
      if MUTATION_WAY == 'ADD':
        reader_skip_sen(reader, sen_conllu)
      continue
    all_test_sen_num +=1
    sen_nlp = PTF_Sen(nlp(sen_conllu.to_doc()), type=NLP_TOOL)
    # print(all_test_sen_num)
    progress_counter.next()
    # print(sen_conllu.to_doc())
    muts = []
    # get mutation sentences
    if MUTATION_WAY == 'ADD':
      mut_sens_ids = sen_conllu.unmask_mut_filter(reader_mut(reader, sen_conllu))
      for mut_sen_id in mut_sens_ids:
        sen_mut = PTF_Sen(nlp(mut_sen_id[0]), type=NLP_TOOL, build_tree=False)
        # dependency filter
        if mut_deprel_type_compare_appendid(sen_nlp, sen_mut, mut_sen_id[1]):
          muts.append((sen_mut, mut_sen_id[1]))
    elif MUTATION_WAY =='DEL':
      # mutation sens check del
      mut_sen_del = sen_nlp.mutation_del_part()
      for sen_del in mut_sen_del:
        sen_mut = PTF_Sen(nlp(sen_del['sen']), type=NLP_TOOL, build_tree=False)
        muts.append((sen_mut, sen_del['del']))
    
    ori_sen_doc = sen_conllu.to_doc()
    # for every filtered mutation sentence
    for mut in muts:
      filtered_mut_num += 1
      mut_sen_doc = mut[0].to_doc()
      if MUTATION_WAY == 'ADD':
        if simple_compare_pos(sen_conllu, sen_nlp):
          c_n_same_sen_num += 1
          res = mut_pos_compare_appendid_res(sen_nlp, mut[0], mut[1])
          if len(res) > 0:
            cnm_100_num += accumulate_error_by_res(error_map_tag_100, res, ori_sen_doc, mut_sen_doc)
        else:
          res = mut_pos_compare_appendid_res(sen_nlp, mut[0], mut[1])
          if len(res) == 0:
            res = mut_pos_compare_appendid_res(sen_conllu, mut[0], mut[1])
            cnm_010_num += accumulate_error_by_res(error_map_tag_010, res, ori_sen_doc, mut_sen_doc)
          else:
            if mut_pos_compare_appendid(sen_conllu, mut[0], mut[1]):
              cnm_001_num += accumulate_error_by_res(error_map_tag_001, res, ori_sen_doc, mut_sen_doc)
            else:
              cnm_000_num += accumulate_error_by_res(error_map_tag_000, res, ori_sen_doc, mut_sen_doc)

      elif MUTATION_WAY =='DEL':
        if simple_compare_pos(sen_conllu, sen_nlp):
          c_n_same_sen_num += 1
          res = del_mut_pos_compare_res(sen_nlp, mut[0], mut[1])
          if len(res) > 0:
            cnm_100_num += accumulate_error_by_res(error_map_tag_100, res, ori_sen_doc, mut_sen_doc)
        else:
          res = del_mut_pos_compare_res(sen_nlp, mut[0], mut[1])
          if len(res) == 0:
            res = del_mut_pos_compare_res(sen_conllu, mut[0], mut[1])
            cnm_010_num += accumulate_error_by_res(error_map_tag_010, res, ori_sen_doc, mut_sen_doc)
          else:
            if del_mut_pos_compare(sen_conllu, mut[0], mut[1]):
              cnm_001_num += accumulate_error_by_res(error_map_tag_001, res, ori_sen_doc, mut_sen_doc)
            else:
              cnm_000_num += accumulate_error_by_res(error_map_tag_000, res, ori_sen_doc, mut_sen_doc)
  progress_counter.finish()

  info_row = [all_test_sen_num, c_n_same_sen_num, filtered_mut_num, cnm_100_num, cnm_000_num, cnm_001_num, cnm_010_num]
  #test end, now output
  csv_filename = time.strftime("results/%Y%m%d-%H%M%S-100-" + NLP_TOOL + '-' + CORPUS_PATH.split('/')[-1].split('.')[0] + '-' + MUTATION_WAY,time.localtime())+'.csv'
  map_to_csv(csv_filename, error_map_tag_100, info_row)
  # csv_filename = time.strftime("results/%Y%m%d-%H%M%S-000-" + CORPUS_PATH.split('/')[-1].split('.')[0] + '-' + MUTATION_WAY,time.localtime())+'.csv'
  # map_to_csv(csv_filename, error_map_tag_000, info_row)
  # csv_filename = time.strftime("results/%Y%m%d-%H%M%S-001-" + CORPUS_PATH.split('/')[-1].split('.')[0] + '-' + MUTATION_WAY,time.localtime())+'.csv'
  # map_to_csv(csv_filename, error_map_tag_001, info_row)
  # csv_filename = time.strftime("results/%Y%m%d-%H%M%S-010-" + CORPUS_PATH.split('/')[-1].split('.')[0] + '-' + MUTATION_WAY,time.localtime())+'.csv'
  # map_to_csv(csv_filename, error_map_tag_010, info_row)