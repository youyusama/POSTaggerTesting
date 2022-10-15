import stanza
import os
from config import *

#load stanza
nlp = stanza.Pipeline('en', r'nlp-models/stanzamodel/stanza_model/', processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
#create output file

doc = nlp('Which specific elements of specific performance artworks do they focus on ?')
# print(doc.sentences[0].words)

print(*[f'id: {word.id}\tword: {word.text}\tupos: {word.upos}\thead id: {word.head}\thead: {sent.words[word.head-1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}' for sent in doc.sentences for word in sent.words], sep='\n')
if not os.path.exists(RESULT_FILE_PATH):
    os.mkdir(RESULT_FILE_PATH)