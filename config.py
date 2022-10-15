# =================================================================================
# config.py used to provide configuation for the main script modifier_mutation.py
# =================================================================================

# the path of corpus that you want test on
# 'test.conllu' is a small corpus in .conllu format, you could leave it as the default first to test whether the code can run correctly, then on other big scale corpura
CORPUS_PATH = 'en_pud-ud-test.conllu'

# the way of mutation, corresponding to the deletion manipulation and the addition manipulation
MUTATION_WAY = 'ADD' # 'DEL' or 'ADD'
# the num of sentences that MLM unmasked, needed when MUTATION_WAY = 'ADD'
# too big will lead the long processing time, 10 is good ;)
UNMASK_NUM = 10
# mutation times
MUTATION_TIMES = 1

# the NLP pipeline you want to test
NLP_TOOL = 'stanza' # 'stanza' or 'spaCy'

# the path of the stanza nlp model file, needed when NLP_TOOL = 'stanza'
# information of the stanza installation and the download of model can be get from https://stanfordnlp.github.io/stanza/usage.html
STANZA_MODEL_PATH = 'nlp-models/stanzamodel/stanza_model/'
# the name of the spaCy nlp model, needed when NLP_TOOL = 'spaCy'
# information of the spaCy installation and the download of model can be get from https://spacy.io/usage
SPACY_MODEL_NAME = 'en_core_web_trf'

# result file path
RESULT_FILE_PATH = 'acl_results/'
STOP_ERROR_NUM = -1
RESULT_LANGUAGE = 'en'
SKIP_SEED = 1

def set_configs(args):
  global CORPUS_PATH
  global MUTATION_WAY
  global UNMASK_NUM
  global MUTATION_TIMES
  global NLP_TOOL
  global STANZA_MODEL_PATH
  global SPACY_MODEL_NAME
  global STOP_ERROR_NUM
  global RESULT_LANGUAGE
  global SKIP_SEED
  CORPUS_PATH = args.corpus
  MUTATION_WAY = args.mutation
  UNMASK_NUM = args.bertnum
  MUTATION_TIMES = args.mutationtimes
  NLP_TOOL = args.tagger
  STANZA_MODEL_PATH = args.modelpathofstanza
  SPACY_MODEL_NAME = args.modelnameofspaCy
  STOP_ERROR_NUM = args.stoperrornum
  RESULT_LANGUAGE = args.language
  SKIP_SEED = args.seed