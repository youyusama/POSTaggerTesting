# POSTman

## Packages needed
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
```
postman.py -h
```