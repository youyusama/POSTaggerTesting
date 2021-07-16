import stanza
import conllu
import io
import time

#load corpus
data = io.open(r'/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-test.conllu', "r", encoding="utf-8")
#load stanza
nlp = stanza.Pipeline('en', r'/mnt/hd0/POStaggingFuzzing/nlp-models/stanzamodel/stanza_model/', processors='tokenize,pos', tokenize_pretokenized=True)
#create output file
filename = time.strftime("%Y%m%d-%H%M%S-",time.localtime())+'result.txt'
outputfile = io.open(str('results/' + filename), "w+", encoding="utf-8")

#create error_map
tag_list_U = ('ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X')
error_map= {}
for key in tag_list_U:
  error_map[key]={}
  for key2 in tag_list_U:
    error_map[key][key2]=0

#filter output
filter_pairs = (('CCONJ', 'SYM'),)

index = 0#sentence num
wrong_sentence = 0
tag = 0#tag num
wrong_tag = 0

#for sentence in corpus
for sentence_conllu in conllu.parse_incr(data):
  nlp_wrong = False
  filter_flag = False
  message = []
  doc = ' '.join([token['form'] for token in sentence_conllu])
  nlpresult = nlp(doc)
  for sentence_nlp in nlpresult.sentences:
    word_id = 0
    for word in sentence_nlp.words:
      tag += 1
      corpus_tag = sentence_conllu[word_id]['upos']
      nlp_tag = word.upos
      if corpus_tag != nlp_tag and corpus_tag in tag_list_U:
        nlp_wrong = True
        wrong_tag += 1
        error_map[corpus_tag][nlp_tag] += 1
        if (corpus_tag, nlp_tag) in filter_pairs:
          filter_flag = True
          message.append((word.text, corpus_tag, nlp_tag))
      word_id += 1
  if nlp_wrong:
    wrong_sentence += 1
    if filter_flag:
      outputfile.write("\n\nsentence:---------------------------------------------------------------------------------------\n"+ doc)
      outputfile.write("\nworng message: " + str(message))
      outputfile.write('\ncorpus:\n' + str([ (token['form'],token['upos']) for token in sentence_conllu]))
      for sentence_nlp in nlpresult.sentences:
        outputfile.write('\nnlp:\n' + str([ (word.text,word.upos) for word in sentence_nlp.words]))
  index += 1
  if index % 500 ==0:
    print(index)


#status in console
print("sentences num: " + str(index))
print("wrong_sentence rate: " + str(wrong_sentence/index))
print("wrong_tag rate: " + str(wrong_tag/tag))

print("process y as x:\n")
print('-\\-',end='')
for key in error_map.keys():
  print('\t'+str(key),end=' ')
print('')
for key in error_map.keys():
  print(str(key), end='\t')
  for key2 in error_map[key].keys():
    print(str(error_map[key][key2]), end='\t')
  print('')
