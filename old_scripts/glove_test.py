print('loading model...', end='')
# from gensim.scripts.glove2word2vec import glove2word2vec
# glove_file = '/mnt/hd0/POStaggingFuzzing/nlp-models/glove/glove.6B.100d.txt'
w2v_file = '/mnt/hd0/POStaggingFuzzing/nlp-models/glove/glove.6B.100d.w2v.txt'
# glove2word2vec(glove_file, w2v_file)
from gensim.models import KeyedVectors

glove_model = KeyedVectors.load_word2vec_format(w2v_file, binary=False)
print('ok')
print(glove_model.most_similar('man', topn=2000)[1900:1950])