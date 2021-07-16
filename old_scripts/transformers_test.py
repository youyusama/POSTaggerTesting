from transformers import pipeline, set_seed

unmasker = pipeline('fill-mask', model='bert-large-cased', top_k = 10)
# generator = pipeline('text-generation', model='gpt2-large')
# unmasker = pipeline('fill-mask', model='bert-base-uncased')
# generator = pipeline('text-generation', model='gpt2')

#This term is qualified by a further concept called a junction which represents one idea , expressed by means of two or more elements , whereas a nexus combines two ideas .
sen = 'I have a change in plans next [MASK] week .'

set_seed(123)

sens = unmasker(sen)
for onesen in sens:
  print('---------')
  print(onesen)
  # gens = generator(onesen['sequence'], num_return_sequences=5, pad_token_id=50256)
  # for gen in gens:
  #   print(gen['generated_text'])
    