from PTF_Sen import *
import conllu
import io
import time
import stanza

#load corpus
corpus = io.open(r'/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-train.conllu', "r", encoding="utf-8")
#load stanza
nlp = stanza.Pipeline('en', r'/mnt/hd0/POStaggingFuzzing/nlp-models/stanzamodel/stanza_model/', processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
#create output file
filename = time.strftime("results/classify-bert-deprel-%Y%m%d-%H%M%S-",time.localtime())+'.txt'
outputfile = io.open(str(filename), "w+", encoding="utf-8")

#create error_map
tag_list_U = ('ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X')
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

for sen in conllu.parse_incr(corpus):
  # short sen unwanted
  if len(sen) <= 5:
    continue
  
  sen_conllu = PTF_Sen(sen, type='conllu')
  sen_stanza = PTF_Sen(nlp(sen_conllu.to_doc()).sentences[0].words)
  # mutation when pos and deprel are allright
  if simple_compare_pos(sen_conllu, sen_stanza):
    ori_sen_num += 1
    print(ori_sen_num)
    error_info = {}

    # # mutation sens can be easily check
    # mut_sens = sen_conllu.mutation_add_next_sen()
    # mut_num += len(mut_sens)
    # for mut_sen in mut_sens:
    #   temp_res = simple_compare_pos_res(sen_conllu, PTF_Sen(nlp(mut_sen).sentences[0].words))
    #   if len(temp_res) > 0:
    #     for error_i in temp_res:
    #       add_error(error_info, error_i, mut_sen)

    # # mutation sens check by dict
    # # mut_sens = sen_conllu.mutation_clause_exchange()
    # # mut_sens += sen_conllu.mutation_add_comma()
    # mut_sens = sen_conllu.mutation_del_part()
    # # mut_sens += sen_conllu.mutation_add_nonsense()
    # # mut_sens += sen_conllu.mutation_exchange_and()
    # mut_num += len(mut_sens)
    # for mut_sen in mut_sens:
    #   temp_res = mut_pos_compare_res(sen_conllu, PTF_Sen(nlp(mut_sen).sentences[0].words))
    #   if len(temp_res) > 0:
    #     for error_i in temp_res:
    #       add_error(error_info, error_i, mut_sen)
    
    # # mutation sens check del
    # mut_sen_del = sen_conllu.mutation_del_part()
    # mut_num += len(mut_sen_del)
    # for sen_del in mut_sen_del:
    #   temp_res = del_mut_pos_compare_res(sen_conllu, PTF_Sen(nlp(sen_del['sen']).sentences[0].words), sen_del['del'])
    #   if len(temp_res) > 0:
    #     for error_i in temp_res:
    #       add_error(error_info, error_i, sen_del['sen'])

    # # mutation sens check append id
    # mut_sens_ids = sen_conllu.mutation_bert_insert_word_filtered()
    # mut_num += len(mut_sens_ids)
    # for mut_sen_id in mut_sens_ids:
    #   temp_res = mut_pos_compare_appendid_res(sen_conllu, PTF_Sen(nlp(mut_sen_id[0]).sentences[0].words), mut_sen_id[1])
    #   if len(temp_res) > 0:
    #     for error_i in temp_res:
    #       add_error(error_info, error_i, mut_sen_id[0])

    # mutation sens check append id
    mut_sens_ids = sen_conllu.mutation_bert_insert_word()
    mut_num += len(mut_sens_ids)
    for mut_sen_id in mut_sens_ids:
      temp_res = mut_pos_compare_appendid_deprel_persent_res(sen_conllu, PTF_Sen(nlp(mut_sen_id[0]).sentences[0].words), mut_sen_id[1])
      if len(temp_res) > 0:
        for error_i in temp_res:
          add_error(error_info, error_i, mut_sen_id[0])

    if error_info != {}:
      for key in error_info:
        ori_sen = sen_conllu.to_doc()
        mut_wrong_num += 1
        # outputfile.write('-------------------------------------------------------------------------------\n')
        # outputfile.write(  'original sen: ' + sen_conllu.to_doc() + '\n')
        # outputfile.write(  'wrong word:   ' + key + '\n')
        for e_i in error_info[key]:
          # outputfile.write('wrong pos:    ' + e_i[0] + ' -> ' + e_i[1] + '\n')
          # outputfile.write('wrong sen:    ' + e_i[2] + '\n')
          if ori_sen in error_map_tag[e_i[0]][e_i[1]]:
            if key in error_map_tag[e_i[0]][e_i[1]][ori_sen]:
              error_map_tag[e_i[0]][e_i[1]][ori_sen][key].append(e_i[2])
            else:
              error_map_tag[e_i[0]][e_i[1]][ori_sen][key] = [e_i[2]]
          else:
            error_map_tag[e_i[0]][e_i[1]][ori_sen] = {key: [e_i[2]]}



outputfile.write('ori_sen_num: ' + str(ori_sen_num) + '\n')
outputfile.write('mut_num: ' + str(mut_num) + '\n')
outputfile.write('mut_wrong_num: ' + str(mut_wrong_num) + '\n')

#print by class
for key in tag_list_U:
  for key2 in tag_list_U:
    outputfile.write('\n-------------------------------------------------------------------------------\n')
    outputfile.write('pos from ' + pos_ch[key] + ' to ' + pos_ch[key2] + '\n')
    for ori_sen in error_map_tag[key][key2]:
      outputfile.write(    'sentence: ' + ori_sen + '\n')
      for word in error_map_tag[key][key2][ori_sen]:
        outputfile.write('wrong word: ' + word + '\n')
        for mut_sen in error_map_tag[key][key2][ori_sen][word]:
          outputfile.write('mut sen:  ' + mut_sen + '\n')
      outputfile.write('---\n')