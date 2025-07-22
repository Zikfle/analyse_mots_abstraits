# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-01-28
# Description: Annotation automatique des données du corpus French Corpa CHILDES
# MIT License
# ---------------------------------------------------------

### Importing strandard library
import os
#import re
#import pickle
#import json 
from tqdm import tqdm
import pandas as pd
import regex as re


# ---------------------------------------------------------
# Data management
# ---------------------------------------------------------

print('---------------------------------------------------------')
print('Reading the DataFrame')
print('---------------------------------------------------------')

#get working path
cur_path = os.path.abspath(os.getcwd())
data_path = os.path.join(cur_path, "data")
module_path = os.path.join(cur_path, "annotation")

#import the main corpus datafile
df = pd.read_csv(os.path.join(data_path, "french_corpa_parsed.csv"), sep = '\t', encoding='utf-8')
#df.index.name = 'id'
#print(df.columns)

#all_corpus = ['Champaud' 'Geneva' 'GoadRose' 'Hammelrath' 'Hunkeler' 'Leveille' 'Lyon'
# 'Palasis' 'Paris' 'StanfordFrench' 'VionColas' 'Yamaguchi' 'York']


#filter 2 corpus out of the data
df = df.loc[df['corpus'] != ('GoadRose')] #pas de LAE + QC
df = df.loc[df['corpus'] != ('Hammelrath')] #story board
df = df.loc[df['corpus'] != ('StanfordFrench')] #pas de transcription
df = df.loc[df['corpus'] != ('VionColas')] # story


#print(df)

#create a list of all role


print('---------------------------------------------------------')
print('Getting the tokenisation from CLAN mor analysis')
print('---------------------------------------------------------')


ids,lemsents,possents,flexions,n_tokens = [],[],[],[],[]


def tokenize_chat(morpho):
    list_grapheme2 = morpho.split(' ')
    lemma_sent = []
    pos_sent = []
    flex_sent = []
    for grapheme in list_grapheme2:
        list_token = grapheme.split('$')
        for token_pos in list_token:
            flexion = 'X'
            token_pos = token_pos.split('|')
            if len(token_pos) > 1:
                pos = token_pos[0]
                token_flexion = token_pos[1]
                token_flexion = re.split(r'[&-]', token_flexion, maxsplit=1)
                if len(token_flexion) > 1:
                    flexion = token_flexion[1]
                    token = token_flexion[0]
                else:
                    flexion = 'X'
                    token = token_flexion[0]
                
            else:
                pos = 'X'
                token = token_pos[0]
            lemma_sent.append(token)
            pos_sent.append(pos)
            flex_sent.append(flexion)

    return [lemma_sent,pos_sent,flex_sent]

for index, row in tqdm(df.iloc[:].iterrows(),total=df.shape[0]):
    id = row['id']
    morpho = str(row['mor'])
    uter = str(row['utterance'])
    tokenized = tokenize_chat(morpho)
    ids.append(id)
    lemsents.append(tokenized[0])
    possents.append(tokenized[1])
    flexions.append(tokenized[2])
    n_tokens.append(len(tokenized[0])-1)

        
print('---------------------------------------------------------')
print('Merging result and saving')
print('---------------------------------------------------------')

# putting the generated list in one dictionnary
df_final = {'id': ids, 'lemme': lemsents, 
            'POS': possents, 'flexions' : flexions , 'n_token': n_tokens}
#'syllable': sylsents, 'nb_syllable': n_sylsents,

dataresult = pd.DataFrame(df_final) # putting the dictionnary into a Datafile
print('Nb de linge dans data_initial :', len(df))
print('Nb de ligne dans data_final :', len(dataresult))


datafinal = pd.merge(df, dataresult, on="id") #merging the initial data and the result data
del datafinal['id']
datafinal.index.name = 'id'
print(datafinal)

datafinal.to_csv('fench_corpa_tokenise.csv', sep = '\t', encoding='utf-8') # saving the Datafile

print(datafinal.columns)

print('---------------------------------------------------------')
print('Saving successful')
print('---------------------------------------------------------')
