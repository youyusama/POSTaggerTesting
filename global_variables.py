NLP_MODEL_PATH = '/mnt/hd0/POStaggingFuzzing/nlp-models/'
UPOS_TAG_LIST = ('ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X')
UNWANTED_ERRORS = [
  (
    ('ADJ', 'VERB'),
    ('VERB', 'ADJ'),
    ('VERB', 'NOUN'),
    ('NOUN', 'VERB'),
  ),(
    ('NOUN', 'PROPN'),
    ('PROPN', 'NOUN'),
    ('PRON', 'DET'),
    ('DET', 'PRON')
  )
]
UPOS_TO_CH = {
'ADJ': '形容',
'ADP': '介词',
'ADV': '副词',
'AUX': '助词',
'CCONJ': '并列连词',
'DET': '定冠',
'INTJ': '感叹',
'NOUN': '名词',
'NUM': '数字',
'PART': '功能',
'PRON': '代词',
'PROPN': '特指名词',
'PUNCT': '标点',
'SCONJ': '从句连词',
'SYM': '符号',
'VERB': '动词',
'X': '其他',
}
XPOS_TO_UPOS = {
  '#'	:	'SYM',
  '$'	:	'SYM',
  '"'	:	'PUNCT',
  ','	:	'PUNCT',
  '-LRB-'	:	'PUNCT',
  '-RRB-'	:	'PUNCT',
  '.'	:	'PUNCT',
  ':'	:	'PUNCT',
  'AFX'	:	'ADJ',
  'CC'	:	'CCONJ',
  'CD'	:	'NUM',
  'DT'	:	'DET',
  'EX'	:	'PRON',
  'FW'	:	'X',
  'HYPH'	:	'PUNCT',
  'IN'	:	'ADP',
  'JJ'	:	'ADJ',
  'JJR'	:	'ADJ',
  'JJS'	:	'ADJ',
  'MD'	:	'VERB',
  'NIL'	:	'X',
  'NN'	:	'NOUN',
  'NNP'	:	'PROPN',
  'NNPS'	:	'PROPN',
  'NNS'	:	'NOUN',
  'PDT'	:	'DET',
  'POS'	:	'PART',
  'PRP'	:	'PRON',
  'PRP$'	:	'DET',
  'RB'	:	'ADV',
  'RBR'	:	'ADV',
  'RBS'	:	'ADV',
  'RP'	:	'ADP',
  'TO'	:	'PART',
  'UH'	:	'INTJ',
  'VB'	:	'VERB',
  'VBD'	:	'VERB',
  'VBG'	:	'VERB',
  'VBN'	:	'VERB',
  'VBP'	:	'VERB',
  'VBZ'	:	'VERB',
  'WDT'	:	'DET',
  'WP'	:	'PRON',
  'WP$'	:	'DET',
  'WRB'	:	'ADV',
  '``'	:	'PUNCT'
}