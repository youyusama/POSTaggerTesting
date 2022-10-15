# POSTman

## Packages needed
process `pip install process`\
conllu `pip install conllu` , when under conda environment use `conda install -c conda-forge conllu`

nlp packages:
```
stanza
spaCy
transformers
```
Installing such NLP framework usually depends on detailed system settings. Simply use `pip install xxx` may not install the package correctlly. It is recommended to follow the official guidelines to install these three packages.

The installation guidelines:
- stanza: https://stanfordnlp.github.io/stanza/#getting-started
- spaCy: https://spacy.io/usage
- transformers: https://huggingface.co/transformers/installation.html

## Installing the NLP models
- stanza: To install the language model of stanza, you can directly run `download_models.py`. See detail info in https://stanfordnlp.github.io/stanza/download_models.html.
- spaCy: To install the language model of spaCy, you should run `python -m spacy download en_core_web_trf` See detail info in https://spacy.io/models.
- transformers: Transformers will detect the model used at runtime and install the model automatically.

## Usage
Run postman with default configuration:
```
postman.py
```
With the default configuration, `stanza` will be used as the POS tagging tool, and the mutation method of deletion `DEL` will be used to test on the pud corpus `.\en_pud-ud-test.conllu`. The result of the test will be saved in folder `.\result\` as a `.csv` file.

See more configuration:
```
postman.py -h
```

## Scripts info
```
bert_sen_gen.py       # unmask module
compare_utilities.py  # the POS,dependency compare functions for mutant
config.py
download_models.py    # script for downloading stanza model
en_pud-ud-test.conllu # the pud corpus, for test
global_variables.py
map2csv.py            # script for output csv file
modifier_mutation.py  # the main body of POSTman
postman.py            # the run script of POSTman
PTF_Err.py            # error class
PTF_Sen.py            # sentence class
test_spaCy.py
test_stanza.py
tool_accuracy_test.py # tool accuracy testing script
unmask_file_reader.py # iteration reader for unmask file
```
## Data
We put test results on the 4 corpora of EWT, GUM, pud, and pronouns in the `.\result\` folder. They also contain our annotation of whether the testing result is a real bug for every token.

The first row of the table contains statistics related to the test. For each error POS tagging on a token, we show its original sentence and mutant sentences. (This means that the POS tagger give different tags to the token on the original sentence and the variant sentence.) These errors are sorted by their type.

The labels at column 3('TP' for ture positive, 'FP' for flase positive, 'IM' for incorrect mutatant) are our manual annotation of the errors.