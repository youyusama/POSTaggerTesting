import nltk

sentences = [
'a group of fish standing in a field',
'a group of fish stand in a field',
'a group of sheep stand in a field',
'a group of deer stand in a field',
'a group of cattle standing in a field',
'a group of cattle stand in a field',
'a group of police stand in a field',
]

for sentence in sentences:
  tokens = nltk.word_tokenize(sentence)
  print(tokens)
  print(nltk.pos_tag(tokens))