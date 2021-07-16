from gensim.models import KeyedVectors
import io
w2v_file = '/mnt/hd0/POStaggingFuzzing/nlp-models/glove/glove.6B.100d.w2v.txt'
glove_model = KeyedVectors.load_word2vec_format(w2v_file, binary=False)
#noun set
noun_set_file = io.open('/mnt/hd0/POStaggingFuzzing/gen_data/noun_set.txt', 'r', encoding='utf-8')
noun_set = {line.strip() for line in noun_set_file.readlines()}
#create output file
filename = '/mnt/hd0/POStaggingFuzzing/gen_data/noun_mutation.txt'
# outputfile = io.open(str(filename), "w+", encoding="utf-8")

minnum = 100
maxnum = 0
nounum = 0
innum = 0
for noun in noun_set:
  tempnum = 0
  if noun in glove_model.vocab:
    innum += 1
    word_similar_list = glove_model.most_similar(noun, topn=2000)
    for word in word_similar_list:
      if word in noun_set:
        print('hey')
        tempnum += 1
  nounum += 1
  if tempnum < minnum:
    minnum = tempnum
  if tempnum > maxnum:
    maxnum = tempnum

print(minnum)
print(maxnum)
print(nounum)
print(innum)