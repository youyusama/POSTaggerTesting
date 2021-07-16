from PTF_Sen import *
import conllu
import io
import time
import stanza
from bert_sens_gen import bert_gen_or_read
from unmask_file_reader import *
import csv
from compare_utilities import *
from global_variables import *

CORPUS_PATH = '/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu'
NLP_MODEL_PATH = '/mnt/hd0/POStaggingFuzzing/nlp-models/'


#load corpus
corpus = io.open(CORPUS_PATH, "r", encoding="utf-8")
#load stanza
nlp = stanza.Pipeline('en', NLP_MODEL_PATH + 'stanzamodel/stanza_model/', processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
#create output file
csv_filename = time.strftime("results/%Y%m%d-%H%M%S-csv-classify-bert",time.localtime())+'.csv'
# outputfile = io.open(str(filename), "w+", encoding="utf-8")

#create error_map
tag_list_U = UPOS_TAG_LIST
error_map_tag= {}
for key in tag_list_U:
  error_map_tag[key]={}
  for key2 in tag_list_U:
    error_map_tag[key][key2]={}

#unwanted errors
unwanted_errors = [
  (
    ('ADJ', 'VERB'),
    ('VERB', 'ADJ'),
    ('VERB', 'NOUN'),
    ('NOUN', 'VERB'),
  ),(
    ('NOUN', 'PROPN'),
    ('PROPN', 'NOUN'),
    ('PRON', 'DET'),
    ('DET', 'PRON')
  )
]

def add_error(error_info, error_i, sen):
  if (error_i.ori_pos, error_i.mut_pos) in unwanted_errors[1]:
    return
  if (error_i.ori_pos, error_i.mut_pos) in unwanted_errors[0] and ( error_i.key.endswith('ed') or error_i.key.endswith('ing') ):
    return
  key_and_id = error_i.key + ' ' + str(error_i.id)
  if key_and_id not in error_info:
    error_info[key_and_id] = [(error_i.ori_pos, error_i.mut_pos, sen)]
  else:
    error_info[key_and_id].append((error_i.ori_pos, error_i.mut_pos, sen))


pos_ch = {
'ADJ': '形容',
'ADP': '介词',
'ADV': '副词',
'AUX': '助词',
'CCONJ': '并列连词',
'DET': '定冠',
'INTJ': '感叹',
'NOUN': '名词',
'NUM': '数字',
'PART': '功能',
'PRON': '代词',
'PROPN': '特指名词',
'PUNCT': '标点',
'SCONJ': '从句连词',
'SYM': '符号',
'VERB': '动词',
'X': '其他',
}

ori_sen_num = 0
mut_num = 0
mut_wrong_num = 0

if __name__ == '__main__':
  # generate the unmask file
  gen_filename = bert_gen_or_read(CORPUS_PATH)
  # iterate reader
  reader = Unmask_File_Reader(gen_filename)

  for sen in conllu.parse_incr(corpus):
    # short sen unwanted
    if len(sen) <= 5:
      reader_skip_sen(reader, sen)
      continue
    sen_conllu = PTF_Sen(sen, type='conllu', build_tree=False)
    sen_stanza = PTF_Sen(nlp(sen_conllu.to_doc()).sentences[0].words)
    if simple_compare_pos(sen_conllu, sen_stanza):
      ori_sen_num += 1
      print(ori_sen_num)
      error_info = {}

      # # mutation sens check del
      # mut_sen_del = sen_stanza.mutation_del_part()
      # mut_num += len(mut_sen_del)
      # for sen_del in mut_sen_del:
      #   temp_res = del_mut_pos_compare_res(sen_stanza, PTF_Sen(nlp(sen_del['sen']).sentences[0].words), sen_del['del'])
      #   if len(temp_res) > 0:
      #     for error_i in temp_res:
      #       add_error(error_info, error_i, sen_del['sen'])
      # mutation sens check append id deprel persent
      unmasks = reader_mut(reader, sen)
      mut_sens_ids = sen_conllu.unmask_mut_filter(unmasks)
      mut_num += len(mut_sens_ids)
      for mut_sen_id in mut_sens_ids:
        sen_mut = PTF_Sen(nlp(mut_sen_id[0]).sentences[0].words, build_tree=False)
        if mut_deprel_compare_appendid(sen_stanza, sen_mut, mut_sen_id[1]):
          temp_res = mut_pos_compare_appendid_res(sen_stanza, sen_mut, mut_sen_id[1])
          if len(temp_res) > 0:
            for error_i in temp_res:
              add_error(error_info, error_i, mut_sen_id[0])
      if error_info != {}:
        for key in error_info:
          ori_sen = sen_conllu.to_doc()
          mut_wrong_num += 1
          for e_i in error_info[key]:
            if ori_sen in error_map_tag[e_i[0]][e_i[1]]:
              if key in error_map_tag[e_i[0]][e_i[1]][ori_sen]:
                error_map_tag[e_i[0]][e_i[1]][ori_sen][key].append(e_i[2])
              else:
                error_map_tag[e_i[0]][e_i[1]][ori_sen][key] = [e_i[2]]
            else:
              error_map_tag[e_i[0]][e_i[1]][ori_sen] = {key: [e_i[2]]}
    else:
      reader_skip_sen(reader, sen)

  with open(csv_filename, 'w', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['ori_sen_num', 'mut_num', 'mut_wrong_num'])
    csv_writer.writerow([ori_sen_num, mut_num, mut_wrong_num])

    # csv by class
    for key in tag_list_U:
      for key2 in tag_list_U:
        csv_writer.writerow([])
        csv_writer.writerow([])
        csv_writer.writerow(['pos from ' + pos_ch[key] + ' to ' + pos_ch[key2] + '\n'])
        for ori_sen in error_map_tag[key][key2]:
          csv_writer.writerow(['original sentence', ori_sen])
          for word in error_map_tag[key][key2][ori_sen]:
            csv_writer.writerow(['wrong word', word])
            for mut_sen in error_map_tag[key][key2][ori_sen][word]:
              csv_writer.writerow(['mutation sentence', mut_sen])
          csv_writer.writerow([])