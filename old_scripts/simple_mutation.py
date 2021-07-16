import stanza
import conllu
import io
import time
import random

#load corpus
corpus = io.open(r'/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-test.conllu', "r", encoding="utf-8")
#load stanza
nlp = stanza.Pipeline('en', r'/mnt/hd0/POStaggingFuzzing/nlp-models/stanzamodel/stanza_model/', processors='tokenize,pos', tokenize_pretokenized=True)
#create output file
filename = time.strftime("results/simple-mutation%Y%m%d-%H%M%S-",time.localtime())+'.txt'
outputfile = io.open(str(filename), "w+", encoding="utf-8")

#create error_map
tag_list_U = ('ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X')
error_map_noun= {}
error_map_sen= {}
for key in tag_list_U:
  error_map_noun[key]=0
  error_map_sen[key]={}
  for key2 in tag_list_U:
    error_map_sen[key][key2]=0

#filter output
filtered_tag = ('PRON', 'PROPN')

#noun set
noun_set_file = io.open('noun_set.txt', 'r', encoding='utf-8')
noun_set = {line.strip() for line in noun_set_file.readlines()}
noun_set_num = len(noun_set)

#config
MUTATION_NUM = 10
random.seed(123)

def mutated_sentences_on_id(sentence, word_id):
  sentences = ''
  for i in range(MUTATION_NUM):
    sentences += ' '.join([(noun_set[random.randint(0, noun_set_num-1)] if token['id'] == word_id else token['form']) for token in sentence]) + ' \n'
  return sentences


mutation_tag_num = 0
mutation_wrong_tag_num = 0
mutated_sen_tag_num = 0
mutated_sen_wrong_tag_num = 0
sentence_num = 0
mutation_wrong_sen_num = 0
for sentence_conllu in conllu.parse_incr(corpus):
  for word in sentence_conllu:
    if word['upos'] == 'NOUN':
      mutation_tag_num += 1
      mutation_word_id = word['id']
      #mutate a noun to other 5 random nouns
      mutated_sentences = mutated_sentences_on_id(sentence_conllu, mutation_word_id)
      #nlp
      nlp_result = nlp(mutated_sentences)
      for sentence_nlp in nlp_result.sentences:
        #sentence error
        word_id = 0
        mutation_sen_wrong = False
        for word_nlp in sentence_nlp.words:
          mutated_sen_tag_num += 1
          corpus_tag = sentence_conllu[word_id]['upos']
          nlp_tag = word_nlp.upos
          if corpus_tag != nlp_tag and corpus_tag in tag_list_U:
            if (corpus_tag, nlp_tag) == ('VERB', 'ADP'):
              print(str(word_nlp.text) + '  ' + str(sentence_conllu[word_id]['form']))
              print(' '.join([token['form'] for token in sentence_conllu]))
              print('nlp:\n' + str([ (word.text,word.upos) for word in sentence_nlp.words]))
            mutated_sen_wrong_tag_num += 1
            error_map_sen[corpus_tag][nlp_tag] += 1
            mutation_sen_wrong = True
          word_id += 1
        if mutation_sen_wrong:
          mutation_wrong_sen_num += 1
        #mutation noun error
        nlp_tag = sentence_nlp.words[mutation_word_id-1].upos
        if nlp_tag != 'NOUN' and nlp_tag not in filtered_tag:
          error_map_noun[nlp_tag] += 1
          mutation_wrong_tag_num += 1
          outputfile.write('\n\n\n--------------------------------------------------------------------------------------------')
          outputfile.write('\noriginal sentence: ' + ' '.join([token['form'] for token in sentence_conllu]))
          outputfile.write('\nmutated sentence:  ' + ' '.join(word.text for word in sentence_nlp.words))
          outputfile.write('\nmutation word ' + str(mutation_word_id) + '('+ word['form'] + ') to ' + nlp_tag + '(' + sentence_nlp.words[mutation_word_id-1].text + ')')
          outputfile.write('\nnlp:\n' + str([ (word.text,word.upos) for word in sentence_nlp.words]))
  sentence_num += 1
  if sentence_num % 100 == 0:
    print(sentence_num)

print('all sentences num: ' + str(mutation_tag_num*MUTATION_NUM))
print('mutation wrong noun tag num: ' + str(mutation_wrong_tag_num))
print('mutation wrong noun tag percent: ' + str(mutation_wrong_tag_num/(mutation_tag_num*MUTATION_NUM)))
print('mutation wrong tag percent: ' + str(mutated_sen_wrong_tag_num/mutated_sen_tag_num))
print('mutation wrong sen num: ' + str(mutation_wrong_sen_num))
print('mutation wrong sen percent: ' + str(mutation_wrong_sen_num/(mutation_tag_num*MUTATION_NUM)))
#sen map
print("process y as x:")
print('-\\-',end='')
for key in error_map_sen.keys():
  print('\t'+str(key),end=' ')
print('')
for key in error_map_sen.keys():
  print(str(key), end='\t')
  for key2 in error_map_sen[key].keys():
    print(str(error_map_sen[key][key2]), end='\t')
  print('')
#noun map
print("\nprocess noun as x:")
print('-\\-',end='')
for key in error_map_noun.keys():
  print('\t'+str(key),end=' ')
print('\n\t',end='')
for key in error_map_noun.keys():
  print(str(error_map_noun[key]), end='\t')