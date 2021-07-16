import spacy

nlp = spacy.load('en_core_web_sm')

doc = nlp('The cells were operating in the Ghazaliyah and al-Jihad districts of the capital.')

for token in doc:
  print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)