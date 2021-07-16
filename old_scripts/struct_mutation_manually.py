import stanza
import conllu
import io
from sen_pos import SenPos, compare_sen_pos

#load stanza
nlp = stanza.Pipeline('en', r'/mnt/hd0/POStaggingFuzzing/nlp-models/stanzamodel/stanza_model/', processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
#read file
# readfile = io.open('gen_data/good_sample_sentences_mutation.txt', "r", encoding="utf-8")

# is_origin_sen = True
# origin_sen = ''
# for line in readfile.readlines():
#   if line == '\n':
#     is_origin_sen = True
#   else:
#     if is_origin_sen:
#       origin_sen = SenPos(nlp(line).sentences[0], sen_type='stanza')
#       is_origin_sen = False
#     else:
#       mutate_sen = SenPos(nlp(line).sentences[0], sen_type='stanza')
#       print('------------------------------------')
#       print(origin_sen.sen)
#       print(mutate_sen.sen)

doc = nlp('Oakland as a city reflects the amazing diversity of its residents and long history .')
print(*[f'id: {word.id}\tword: {word.text}\thead id: {word.head}\thead: {sent.words[word.head-1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}' for sent in doc.sentences for word in sent.words], sep='\n')

doc = nlp('Oakland as a city reflects the amazing diversity .')
print(*[f'id: {word.id}\tword: {word.text}\thead id: {word.head}\thead: {sent.words[word.head-1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}' for sent in doc.sentences for word in sent.words], sep='\n')
