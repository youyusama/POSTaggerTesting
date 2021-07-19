import spacy
from spacy.tokens import Doc
nlp = spacy.load('en_core_web_sm', exclude=['lemmatizer', 'ner'], )
# nlp.tokenizer = nlp.tokenizer.tokens_from_list
# print(nlp.pipe_names)

class WhitespaceTokenizer:
  def __init__(self, vocab):
    self.vocab = vocab

  def __call__(self, text):
    words = text.split(" ")
    spaces = [True] * len(words)
    # Avoid zero-length tokens
    for i, word in enumerate(words):
      if word == "":
        words[i] = " "
        spaces[i] = False
    # Remove the final trailing space
    if words[-1] == " ":
      words = words[0:-1]
      spaces = spaces[0:-1]
    else:
      spaces[-1] = False
    return Doc(self.vocab, words=words, spaces=spaces)

sen = ', Do you want us to come over to the Enron b in your call .'
nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)
doc = nlp(sen)
# doc = Doc(nlp.vocab, words = sen.split(' '))

for token in doc:
  print(token.i, token.text, token.pos_, token.dep_, token.head, token.head.i)