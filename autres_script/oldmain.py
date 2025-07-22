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
import ast
import unicodedata

### Importing nlp library
import pandas as pd
import spacy
import torch
import nltk
nltk.download('omw-1.4')
from nltk.corpus import wordnet

# setting up cuda gpu for spacy
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
spacy.require_gpu()
torch.cuda.set_per_process_memory_fraction(0.7, device=0) #limiting python gpu memory usage to 70%
nlp = spacy.load("fr_dep_news_trf") #importing spacy model: french_medium


# ---------------------------------------------------------
# Data management
# ---------------------------------------------------------


#get working path
cur_path = os.path.abspath(os.getcwd())
data_path = os.path.join(cur_path, "data")
module_path = os.path.join(cur_path, "annotation")

#import the main corpus datafile
df = pd.read_csv(os.path.join(data_path, "data_french_corpa.csv"))
#print(df.columns)

#filter 2 corpus out of the data
df = df.loc[df['corpus_name'] != ('French-Lyon')]
df = df.loc[df['corpus_name'] != ('Geneva')]

#create a list of all speaker_name
all_participant = df['speaker_name'].unique()

#filter the data 1-keep pertinant column 2- keep target child 3-
df = df[['collection_id','transcript_id','corpus_name','utterance_order','speaker_role','speaker_name','gloss','target_child_age']] # keep only pertinant column
df = df.sort_values(by=['collection_id','transcript_id','utterance_order'], ascending=[True, True, True]) # order the row in the chronological order
df = df.loc[df['speaker_role'] == ('Target_Child')] # keep only target child

#create list of all child speaker_name
all_child = df['speaker_name'].unique()

#import valence data into a dictionnairy
valence_df = pd.read_csv(os.path.join(data_path, "data_fan_valence.csv"))
mot_fan = valence_df.iloc[:, 0]
mot_valence = valence_df.iloc[:, 4]
valence_dic = dict(zip(mot_fan[1:], mot_valence[1:]))

#import imageability data into a dictionnairy
imagea_df = pd.read_csv(os.path.join(data_path, "data_semantiqc_imagea.csv"))
mot_semqc = imagea_df.iloc[:, 0]
mot_imagea = imagea_df.iloc[:, 1]
imagea_dic = dict(zip(mot_semqc, mot_imagea))

#import phonetic transcription lexicon
phon_df = pd.read_csv(os.path.join(data_path, "fr_ open_dict_data.csv"))
mot_grapheme = phon_df.iloc[:, 0]
mot_phon = phon_df.iloc[:, 1]
phon_dic = dict(zip(mot_grapheme, mot_phon))



# ---------------------------------------------------------
# Fonctions
# ---------------------------------------------------------


def get_hyperval(lemma):
    synset = wordnet.synsets(lemma, None, 'fra', True)
    hyperscore = None
    if len(synset) != 0:
        #for sens in synset:
            #print(sens)
        premiersynset  = synset[0]
        hyper_path = premiersynset.hypernym_paths()
        #print(hyper_path)
        hyperscore = len(hyper_path[0])
        hyperscore2 = premiersynset.min_depth()
        #print(hyperscore)
    return hyperscore

def get_sem_val(lemma,valence_dic,imagea_dic):
    valence = None
    imagea = None
    if lemma in valence_dic:
        valence = valence_dic[lemma]
    if lemma in imagea_dic:
        imagea = imagea_dic[lemma]
    return [valence,imagea]
    
def get_phonetique(token,phon_dic):
    transcription = None
    if token in phon_dic:
        transcription = phon_dic[token].split(',')
        transcription = transcription[0]
    return transcription

    
def get_phono_patron(word_phon):
    patron = ''
    voyelle = ['i','ə','e','ɛ','a','ɑ','o','ɔ','u','y','ø','œ','ɑ̃','ɛ̃','œ̃','ɔ̃']
    consonne = ['p','b','t','d','k','g',
                'f','v','s','z','ʃ','ʒ',
                'm', 'n', 'ɲ', 'ŋ',
                'l', 'ʁ', 'j', 'w',]
    plosive = ['p', 'b', 't', 'd', 'k', 'g']
    fricative = ['f', 'v', 's', 'z', 'ʃ', 'ʒ']
    nasale = ['m', 'n', 'ɲ', 'ŋ']
    liquide_semi = ['l', 'ʁ', 'j', 'w']
    if word_phon != None:
        word_phon2 = unicodedata.normalize('NFC', word_phon)
        for idx in range(len(word_phon2)):
            caractere = word_phon2[idx]
            if caractere in voyelle:
                patron = patron + 'V'
            elif caractere in consonne:
                patron = patron + 'C'
            elif caractere == '':
                print(f'Unknown caracter from the phonetic input : {caractere}')
                continue
    return patron


# ---------------------------------------------------------
# Main loop
# ---------------------------------------------------------




'''
for index, row in subdf.iloc[0:1000].iterrows():
    uter = row['gloss']
    coll = row['corpus_name']
    coll2 = row['collection_id']
    tran = row['transcript_id']
    order = row['utterance_order']
    uter = str(uter)
    print(uter,coll,coll2,tran,order)
'''


'''
for index, row in tqdm(df.iloc[:1000].iterrows()):
    uter = row['gloss']
    uter = str(uter)
    split_uter = re.split(r" |'|-", uter)
    for word in split_uter:
        hyperscore = get_synval(word)
        print(word)
        print(hyperscore)
'''


score_match = {'total' : 0, 'valence' : 0, 'imagea' : 0, 'hyper' : 0, 'phon' : 0}
stopword = ['xxx' , 'x', 'xx', 'www' , 'nan' , 'yyy' , 'zzz','ouais','-','mm']

phrase,tok,lemm,phon,hyper,val,imag,age = [],[],[],[],[],[],[],[]
dictionnaire = {}


print('---------------------------------------------------------')
print('Running main loop')
print('---------------------------------------------------------')


for index, row in tqdm(df.iloc[:].iterrows(),total=df.shape[0]):
    uter = row['gloss']
    uter = str(uter)
    child_age = row['target_child_age']
    uter_tokenise = nlp(str(uter))
    for token_spacy in uter_tokenise:
        token = token_spacy.text
        lemme = token_spacy.lemma_
        if token in stopword:
            continue
        elif token_spacy.pos_ == 'NOUN':
            score_match['total'] += 1
            hyperscore = get_hyperval(lemme)
            if hyperscore != None:
                score_match['hyper'] += 1
            sem_score = get_sem_val(lemme,valence_dic,imagea_dic)
            valence = sem_score[0]
            imageabilite = sem_score[1]
            if valence != None:
                score_match['valence'] += 1
            if imageabilite != None:
                score_match['imagea'] += 1
            phonetique = get_phonetique(lemme,phon_dic)
            if phonetique != None:
                score_match['phon'] += 1
            phrase.append(uter)
            tok.append(token)
            lemm.append(lemme)
            phon.append(phonetique)
            hyper.append(hyperscore)
            val.append(valence)
            imag.append(imageabilite)
            age.append(child_age)

            if (lemme not in dictionnaire):
                dictionnaire[lemme] = 1
            else:
                dictionnaire[lemme] += 1

print('---------------------------------------------------------')
print('Loop done. Printing and saving results')
print('---------------------------------------------------------')


print(score_match)

sorteddictionairy = dict(reversed(sorted(dictionnaire.items(), key=lambda item: item[1])))
nom = sorteddictionairy.keys()
nb_occu = sorteddictionairy.values()
dico_final = {'Lemme' : nom, "Nombe d'occurence" : nb_occu}

donne_final = {'phrase': phrase, 'token': tok, 'lemme': lemm,
               'phonetique': phon, 'score_hyper': hyper, 'score_valence': val,
                'score_imagea': imag, 'occurence_age': age}

data_dico_final = pd.DataFrame(dico_final)
datafinal = pd.DataFrame(donne_final)
#print(datafinal)

datafinal.to_csv('analyse_mots.csv', sep = ',', encoding='utf-8')
data_dico_final.to_csv('analyse_dico.csv', sep = ',', encoding='utf-8')
