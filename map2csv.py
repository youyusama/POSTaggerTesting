import csv
from global_variables import *

def map_to_csv(csv_filename, error_map, info_row):
  with open(csv_filename, 'w', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['all_test_sen_num', 'c_n_same_sen_num', 'filtered_mut_num', 'cnm_100_num', 'cnm_000_num', 'cnm_001_num', 'cnm_010_num'])
    csv_writer.writerow(info_row)

    # csv by class
    for key in error_map:
      for key2 in error_map:
        csv_writer.writerow([])
        csv_writer.writerow([])
        csv_writer.writerow(['pos from ' + UPOS_TO_CH[key] + ' to ' + UPOS_TO_CH[key2] + '\n'])
        for ori_sen in error_map[key][key2]:
          csv_writer.writerow(['original sentence', ori_sen])
          for word in error_map[key][key2][ori_sen]:
            csv_writer.writerow(['wrong word', word])
            for mut_sen in error_map[key][key2][ori_sen][word]:
              csv_writer.writerow(['mutation sentence', mut_sen])
          csv_writer.writerow([])