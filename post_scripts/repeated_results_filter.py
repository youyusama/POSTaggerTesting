import xlrd as xl
import csv

file_read = 'resultsx/20210828-123135-100-stanza-en_gum-ud-train-ADD.csv'
file_new = 'results/20210923-171604-100-stanza-en_gum-ud-train-ADD.csv'

f_read = csv.reader(open(file_read,'r'))
f_new = csv.reader(open(file_new,'r'))

new_map = {}
type_key = ''
state = 0
now_sentence = ''
now_word = ''
now_mut = []

new_set = set()
for row in f_new:
  if row == []:
    continue
  if row[0] == 'wrong word':
    now_word = row[1]
    new_set.add(type_key+now_sentence+now_word)
  if row[0] == 'mutation sentence':
    now_mut.append(row[1])
  if row[0].startswith('POS tagged wrongly from'):
    type_key = row[0]
  if row[0] == 'original sentence':
    now_sentence = row[1]

for row in f_read:
  if row == []:
    continue
  if row[0] == 'wrong word':
    now_word = row[1]
    if not type_key+now_sentence+now_word in new_set:
      print('111')
  if row[0] == 'mutation sentence':
    now_mut.append(row[1])
  if row[0].startswith('pos from'):
    type_key = row[0].replace('pos from', 'POS tagged wrongly from')
  if row[0] == 'original sentence':
    now_sentence = row[1]

# # load the new csv file
# for row in f_new:
#   if row == []:
#     continue
#   if row[0] == 'wrong word':
#     now_word = row[1]
#   if row[0] == 'mutation sentence':
#     now_mut.append(row[1])
#     state = 1
#   if row[0].startswith('POS tagged wrongly from'):
#     if state == 1:
#       new_map[type_key][now_sentence+','+now_word] = now_mut
#       now_mut = []
#       state = 0
#     type_key = row[0]
#     new_map[type_key] = {}
#   if row[0] == 'original sentence':
#     if state == 1:
#       new_map[type_key][now_sentence+','+now_word] = now_mut
#       now_mut = []
#       state = 0
#     now_sentence = row[1]

# # delete the previous bugs
# for row in f_read:
#   if row == []:
#     continue
#   if row[0] == 'wrong word':
#     now_word = row[1]
#     if now_sentence+','+now_word in new_map[type_key]:
#       del new_map[type_key][now_sentence+','+now_word]
#   if row[0].startswith('pos from'):
#     type_key = row[0].replace('pos from', 'POS tagged wrongly from')
#   if row[0] == 'original sentence':
#     now_sentence = row[1]

# # dict 2 csv
# with open(''.join(file_new.split('.')[0:-1]) + 'removed.csv', 'w', encoding='utf-8') as f:
#   w = csv.writer(f)
#   for key in new_map:
#     w.writerow([key])
#     for sen_and_word in new_map[key]:
#       w.writerow(['original sentence', ','.join(sen_and_word.split(',')[0:-1])])
#       w.writerow(['wrong word', sen_and_word.split(',')[-1]])
#       for mut in new_map[key][sen_and_word]:
#         w.writerow(['mutation sentence', mut])
#       w.writerow([])
#     w.writerow([])