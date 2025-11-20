# Masterthesis

This repository serves as a repository for **replication** of the quantitative results of my masters thesis.

## Requirements

 - An API-key for the archival service of the German Bundestag ([https://dip.bundestag.de/%C3%BCber-dip/hilfe/api#content](https://dip.bundestag.de/%C3%BCber-dip/hilfe/api#content))  
 - german macrodata set from Thomas Picketty's personal website ([http://piketty.pse.ens.fr/fr/capitalisback](http://piketty.pse.ens.fr/fr/capitalisback)).

## Execution Order

Run the jupyter notebooks in the following order:

```
Bundestagsscraper (V2) → KeywordSearch → Preprocessing (V2) → 
Annotation & Processing → Descriptives & OLS → NLP-Analysis
```

<img width="784" height="857" alt="Flowchart-Script-order" src="https://github.com/user-attachments/assets/5ff541a2-9666-4d0e-9785-408faa508337" />

*(own figure)*

## Setup Notes

- To run the replication you need to create a "Speeches" folder containing another "IndividualSpeeches" folder one layer above your scripts folder.
- This approach is clunky and I'll eventually rework it but for the moment it works for the selection of files based on content.
- Some of the scripts are redundant but I left them here to serve as part of my research-diary.

## Minimal Replication Pipeline

The replication requires only the execution of:

1. Bundestagsscraper(V2).ipynb
2. KeywordSearch.ipynb
3. Preprocessing(V2).ipynb
4. Annotation&Processing.ipynb
5. Descriptives_&_OLS.ipynb
6. NLP-Analyisis.ipynb

Overall a very inefficient implementation of my research design but this project is one examplary case of path dependency.
