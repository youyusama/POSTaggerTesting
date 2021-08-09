import spacy
from spacy.tokens import Doc

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

nlp = spacy.load('en_core_web_trf', exclude=['lemmatizer', 'ner'], )

sen = 'Hold the entire chicken down on a flat surface .'
nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)
doc = nlp(sen)

for token in doc:
  print(token.i, token.text, token.pos_, token.dep_, token.head, token.head.i)