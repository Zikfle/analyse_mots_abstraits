# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-01-28
# Description: Annotation automatique des données du corpus French Corpa CHILDES
# MIT License
# ---------------------------------------------------------

### Importing standard library
import os
#import re
#import pickle
#import json 
from tqdm import tqdm
import pandas as pd
import regex as re

# ---------------------------------------------------------
# Fonctions
# ---------------------------------------------------------

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



def parse_token(data_path: str):

    print('---------------------------------------------------------')
    print(f'Reading the DataFrame form {data_path}')
    print('---------------------------------------------------------')
    #import the main corpus datafile
    df = pd.read_csv(data_path, sep = ',', encoding='utf-8')
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

    print('---------------------------------------------------------')
    print('Getting the tokenisation from CLAN mor analysis')
    print('---------------------------------------------------------')

    ids,lemsents,possents,flexions,n_tokens = [],[],[],[],[]

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
    print('Merging result')
    print('---------------------------------------------------------')

    # putting the generated list in one dictionnary
    df_final = {'id': ids, 'lemme': lemsents, 
                'POS': possents, 'flexions' : flexions , 'n_token': n_tokens}
    #'syllable': sylsents, 'nb_syllable': n_sylsents,

    dataresult = pd.DataFrame(df_final) # putting the dictionnary into a Datafile
    print('Nb of line in innital data :', len(df))
    print('Nb of line in final data :', len(dataresult))


    datafinal = pd.merge(df, dataresult, on="id") #merging the initial data and the result data
    del datafinal['id']
    datafinal.index.name = 'id'
    print(datafinal)
    
    return datafinal


# ---------------------------------------------------------
# param
# ---------------------------------------------------------

run_as_test = False
saving = False
save_name = 'french_corpa_token1.csv'

# run main function
if run_as_test == True:

    data_path = 'A://Maitrise-analyse/results/french_corpa_parsed1.csv'
    result_folder_location = 'A://Maitrise-analyse/results'
    datafinal = parse_token(data_path)

    if saving == True:
        print('---------------------------------------------------------')
        print('Saving the result in a csv file')
        print('---------------------------------------------------------')

        #saving the result
        out_file = os.path.join(result_folder_location, save_name)
        if os.path.exists(out_file):
            #  Ask the user if we should overwrite it
            answer = input(f"File '{out_file}' already exists. Overwrite? (y/n): ").strip().lower()
            if not answer.startswith('y'):
                print("Skipping save – user declined to overwrite.")
                # Optionally exit or simply skip the save step
                # sys.exit(0)   # if you really want to abort the script
            else:
                # User consented – proceed with overwrite
                datafinal.to_csv(out_file, sep=',', encoding='utf-8')
                print('---------------------------------------------------------')
                print('Saving successful')
                print('---------------------------------------------------------')
        else:
            datafinal.to_csv(out_file, sep=',', encoding='utf-8')

            print('---------------------------------------------------------')
            print('Saving successful')
            print('---------------------------------------------------------')
    
    else:
        print('---------------------------------------------------------')
        print('Saving set to false')
        print('---------------------------------------------------------')
