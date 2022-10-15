import csv
from global_variables import *
from config import RESULT_LANGUAGE

def map_to_csv(csv_filename, error_map, info_row):
  language_dict = UPOS_TO_EN
  if RESULT_LANGUAGE == 'ch':
    language_dict = UPOS_TO_CH

  with open(csv_filename, 'w', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['time used', '#all seed sentences', '#orignial sentences can be tagged correctly', '#filtered mutants', 
    '#original sentences of mutants can be tagged correctly', '#tokens in mutants', '#tokens are tagged incorrectly in mutants', 
    '#mutants are tagged incorrectly', '# (corpus tag)same as(nlp tag on orignial sentence)differen with(nlp tag on mutant)', 
    '# (corpus tag)(nlp tag on orignial sentence)(nlp tag on mutant) all different', '#(corpus tag)same as(nlp tag on mutant)different with(nlp tag on orignial sentence)', 
    '# (corpus tag)differen with(nlp tag on orignial sentence)same as(nlp tag on mutant)', 'mutation token num 100', 'mutation token wrong num 100', '100 mutation num'])
    csv_writer.writerow(info_row)

    # csv by class
    for key in error_map:
      for key2 in error_map:
        csv_writer.writerow([])
        csv_writer.writerow([])
        csv_writer.writerow(['POS tagged wrongly from ' + language_dict[key] + ' to ' + language_dict[key2] + '\n'])
        for ori_sen in error_map[key][key2]:
          csv_writer.writerow(['original sentence', ori_sen])
          for word in error_map[key][key2][ori_sen]:
            csv_writer.writerow(['wrong word', word])
            for mut_sen in error_map[key][key2][ori_sen][word]:
              csv_writer.writerow(['mutation sentence', mut_sen])
          csv_writer.writerow([])