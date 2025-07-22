# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 18:29:41 2023

@author: Zikfle
"""
from tqdm import tqdm
import pandas as pd
import re
import spacy
import fr_core_news_md
import pickle
import json 
import os
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.cuda.set_per_process_memory_fraction(0.7, device=0)
spacy.require_gpu()

nlp = spacy.load("fr_core_news_md")

def lemme_dict(list_of_utterence):
    """
    takes a list of string
    iterate on each string
    tokenizes and lemmatizes it
    counts the individual lemmas
    returns a dictionary
    """
    print('################')
    print('Compilation du dictionaire')
    print("Nombre d'ennonce' :", len(list_of_utterence))
    dictionnaire = {}

    for phrase in tqdm(list_of_utterence[:10000]):
        stopword = ['xxx' , 'x', 'xx', 'www' , 'nan' , 'yyy' , 'zzz']
        phrase_tokenise = nlp(str(phrase))
        for token in phrase_tokenise:
            lemme = token.lemma_
            if lemme in stopword:
                #print('hit')
                continue
            #if token.pos_ != 'NOUN':
                #continue
            #print(type(lemme))
            if (lemme not in dictionnaire):
                dictionnaire[lemme] = 1
            else:
                dictionnaire[lemme] += 1
             
            

    return dictionnaire

def brute_dict(list_of_utterence):
    """
    takes a raw text file
    tokenizes it
    counts the individual token
    returns a dictionary
    """
    print('################')
    print('Compilation du dictionaire')
    dictionnaire = {}
    stopword = ['xxx' , 'x', 'xx', 'www' , 'nan' , 'yyy' , 'zzz']
    for phrase in tqdm(list_of_utterence[:]): #[:]
        phrase_tokenise = re.split(r"[ '+'\s]+", str(phrase))
        for token in phrase_tokenise:
            if token in stopword:
                continue
            #print(token)
            lemme = token
            if (lemme not in dictionnaire):
                dictionnaire[lemme] = 1
            else:
                dictionnaire[lemme] += 1
             

    return dictionnaire




df = pd.read_csv('Data - corpus_french.csv')
#print(df)
print(df.columns)
#df = df[['gloss', 'num_tokens','speaker_code','speaker_name', 'target_child_age','corpus_name']]
#df = df.loc[df['gloss'] != ('xxx' or 'www' or 'nan' or 'yyy' or ' ')]
df = df.loc[df['corpus_name'] != ('French-Lyon')]
df = df.loc[df['corpus_name'] != ('Geneva')]
all_participant = df['speaker_name']
#print(all_participant)

all_utterances = df['gloss']

chi_df = df.loc[df['speaker_role'] == ('Target_Child')]
adt_df = df.loc[df['speaker_role'] != ('Target_Child' or 'Child' or 'Girl' or 'Boy')]

all_corpus = []

for corpus in df['corpus_name']:
    if corpus not in all_corpus:
        all_corpus.append(corpus)

all_role =[]


for role in df['speaker_role']:
    if role not in all_role:
        all_role.append(role)

#print(chi_df['speaker_role'])
#print(adt_df['speaker_role'])

all_child_utterances = chi_df['gloss']

nb_token_chi = chi_df['num_tokens'].sum()
nb_token_adt = adt_df['num_tokens'].sum()
nb_token = df['num_tokens'].sum()
nb_ennonce_chi = len(chi_df)
nb_ennonce_adt = len(adt_df)
nb_ennonce = len(all_utterances)



print('###########')

print(f"Liste des corpus : {all_corpus}")
print(f"Liste des roles : {all_role}")


print(f"Nombre de token enfant : {nb_token_chi}")
print(f"Nombre d'énnoncé enfant : {nb_ennonce_chi}")

print(f"Nombre de token Adute : {nb_token_adt}")
print(f"Nombre d'énnoncé Adulte : {nb_ennonce_adt}")


print(f"Nombre de token Total : {nb_token}")
print(f"Nombre d'énnoncé Total : {nb_ennonce}")

#dictionnaire
final_dictionnaire = lemme_dict(all_child_utterances)
#final_dictionnaire = brute_dict(all_child_utterances)

# Sorted Dictionary
sorteddictionairy = dict(sorted(final_dictionnaire.items(), key=lambda item: item[1]))
#print(sorteddictionairy)

print('############')
print('Nombre de lemme :', len(final_dictionnaire))

'''
with open('dico.json', 'w', encoding='utf-8') as convert_file: 
     json.dump(sorteddictionairy, convert_file, ensure_ascii=False)
'''




