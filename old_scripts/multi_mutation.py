from sen_mut import SenMut, mut_pos_compare, mut_pos_compare_res
from sen_ori import SenOri, sen_pos_compare, is_dep_same, is_pos_dep_same, is_pos_same
import conllu
import io
import time
import stanza

#load corpus
corpus = io.open(r'/mnt/hd0/POStaggingFuzzing/corpus/ud-treebanks-v2.7/UD_English-GUM/en_gum-ud-test.conllu', "r", encoding="utf-8")
#load stanza
nlp = stanza.Pipeline('en', r'/mnt/hd0/POStaggingFuzzing/nlp-models/stanzamodel/stanza_model/', processors='tokenize,mwt,pos,lemma,depparse', tokenize_pretokenized=True)
#create output file
filename = 'results/multi_mutation.txt'
outputfile = io.open(str(filename), "w+", encoding="utf-8")


sen_num = 0
mut_num = 0
mut_wrong_num = 0

for sen in conllu.parse_incr(corpus):
  sen_conllu = SenOri(sen, 'conllu')
  sen_nlp = nlp(sen_conllu.to_doc()).sentences[0]
  sen_stanza = SenOri(sen_nlp, 'stanza')
  if is_pos_same(sen_conllu, sen_stanza):
    sen_num += 1
    sen_mut = SenMut(sen_nlp.words)
    mut_res = sen_mut.mutation_clause_exchange()
    mut_res += sen_mut.mutation_add_comma()
    mut_res += sen_mut.mutation_del_part()
    mut_res += sen_mut.mutation_add_nonsense()
    mut_res += sen_mut.mutation_exchange_and()
    mut_num += len(mut_res)
    for mut in mut_res:
      mut_mut = SenMut(nlp(mut).sentences[0].words)
      if not mut_pos_compare(sen_mut, mut_mut):
        mut_wrong_num += 1
        outputfile.write('----------------------------------------------------------------------\n')
        outputfile.write('orignal sentence: ' + sen_mut.to_doc() + '\n')
        outputfile.write('mutated sentence: ' + mut + '\n')
        outputfile.write('differences: ' + str(mut_pos_compare_res(sen_mut, mut_mut)) + '\n')

print(sen_num)
print(mut_num)
print(mut_wrong_num)