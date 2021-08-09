import stanza

#load stanza
nlp = stanza.Pipeline('en', r'/mnt/hd0/POStaggingFuzzing/nlp-models/stanzamodel/stanza_model/', processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
#create output file

doc = nlp('"As part of New Zealand , there are no passport or visa requirements and no border controls on arrival from the mainland country ."')
# print(doc.sentences[0].words)

print(*[f'id: {word.id}\tword: {word.text}\tupos: {word.upos}\thead id: {word.head}\thead: {sent.words[word.head-1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}' for sent in doc.sentences for word in sent.words], sep='\n')