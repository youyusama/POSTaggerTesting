import argparse
from config import set_configs


parser = argparse.ArgumentParser(description='Part-of-Speech Testing')
parser.add_argument('-c', '--corpus', default='en_pud-ud-test.conllu', help='corpus\
   in .conllu format, you could leave it as the default first to test whether the code can run correctly, then on other big scale corpura')
parser.add_argument('-m', '--mutation', choices=['ADD', 'DEL'], default='DEL', help='the \
  way of mutation, corresponding to the deletion manipulation and the addition manipulation')
parser.add_argument('-n', '--bertnum', type=int, default=10, help='the num of sentences that\
   MLM unmasked, used when MUTATION_WAY is ADD, too big will lead the long processing time, 10 is good ;)')
parser.add_argument('-t', '--tagger', choices=['stanza', 'spaCy'], default='stanza', help='the POS tagging tool used')
parser.add_argument('-sp', '--modelpathofstanza', default='nlp-models/stanzamodel/stanza_model/', help='the path \
  of the stanza nlp model file, used when NLP_TOOL is stanza information of the stanza installation and the download of model can be get from https://stanfordnlp.github.io/stanza/usage.html')
parser.add_argument('-am', '--modelnameofspaCy', default='en_core_web_trf', help='the name of the \
  spaCy nlp model, used when NLP_TOOL is spaCy, information of the spaCy installation and the download of model can be get from https://spacy.io/usage')

args = parser.parse_args()

set_configs(args)

from modifier_mutation import mm
mm()