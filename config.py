# =================================================================================
# config.py used to provide configuation for the main script modifier_mutation.py
# =================================================================================

# the path of corpus that you want test on
# 'test.conllu' is a small corpus in .conllu format, you could leave it as the default first to test whether the code can run correctly, then on other big scale corpura
CORPUS_PATH = 'test.conllu'

# the way of mutation, corresponding to the deletion manipulation and the addition manipulation
MUTATION_WAY = 'ADD' # 'DEL' or 'ADD'
# the num of sentences that MLM unmasked, needed when MUTATION_WAY = 'ADD'
# too big will lead the long processing time, just leaving it as 10 is good ;)
UNMASK_NUM = 6

# the NLP pipeline you want to test
NLP_TOOL = 'spaCy' # 'stanza' or 'spaCy'

# the path of the stanza nlp model file, needed when NLP_TOOL = 'stanza'
# information of the stanza installation and the download of model can be get from https://stanfordnlp.github.io/stanza/usage.html
STANZA_MODEL_PATH = 'nlp-models/stanzamodel/stanza_model'
# the name of the spaCy nlp model, needed when NLP_TOOL = 'spaCy'
# information of the spaCy installation and the download of model can be get from https://spacy.io/usage
SPACY_MODEL_NAME = 'en_core_web_trf'