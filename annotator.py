# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-01-28
# Description:  Automatic anotation of data from corpus French Corpa CHILDES
#               Annotation automatique des données du corpus French Corpa CHILDES
# MIT License
# ---------------------------------------------------------

### Importing strandard library
import os #for file managment
#import re
#import pickle
#import json 
from tqdm import tqdm #for progress bar
import pandas as pd #for dataframe management
import math
import ast #for reading string as list
import unicodedata #for reading string as unicode

### Importing nlp library
import nltk #for using wordnet
nltk.download('omw-1.4') #making sure wordnet is installed
from nltk.corpus import wordnet
import statistics


# ---------------------------------------------------------
# Data management
# ---------------------------------------------------------


#get working path
cur_path = os.path.abspath(os.getcwd())
data_path = os.path.join(cur_path, "data")
result_path = os.path.join(cur_path, "resultats")

#import the main corpus datafile
df = pd.read_csv(os.path.join(result_path, "fench_corpa_tokenise.csv"), sep = '\t', encoding='utf-8')
#print(df.columns)

#create a list of all speaker_role
all_role = df['role'].unique()

#filter the data - keep overheard speech
all_role = ['Target_Child', 'Mother', 'Brother', 'Father', 'Sister', 'Visitor', 'Relative',
 'Investigator', 'Unidentified', 'Boy', 'Caretaker', 'Teenager', 'Grandmother',
 'Child', 'Adult', 'Grandfather', 'Girl', 'Media', 'Playmate', 'Teacher',       
 'Friend', 'Student']

other_role = ['Mother', 'Brother', 'Father', 'Sister', 'Visitor', 'Relative',
 'Investigator', 'Unidentified', 'Boy', 'Caretaker', 'Teenager', 'Grandmother',
 'Adult', 'Grandfather', 'Girl', 'Media', 'Playmate', 'Teacher',       
 'Friend', 'Student'] # removing child and target_child

df_other = df[df['role'].isin(other_role)]

#filter the data - keep target child
filtre = "df = df.loc[df['role'] == ('Target_Child')]"
df = df.loc[df['role'] == ('Target_Child')]

all_corpus = df['corpus'].unique()
print(sorted(all_corpus))

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

#import lexicon (lexique382)
lex3_df = pd.read_csv(os.path.join(data_path,'data_lexique382.tsv'), sep='\t', header=0)
lex3_noun_df = lex3_df.loc[lex3_df['cgram'] == ('NOM')] #filter and keep only noun
mot_grapheme = lex3_noun_df.iloc[:, 0]
mot_grapheme = [str(x) for x in mot_grapheme]
mot_grapheme = list(map(str.lower,mot_grapheme)) # disregard character case of grapheme in the dic
mot_phon = lex3_noun_df.iloc[:, 1]
n_syll = lex3_noun_df.iloc[:, 23]
patern_phon = lex3_noun_df.iloc[:, 24]
freqfilms2 = lex3_noun_df.iloc[:, 6]
freqlivres = lex3_noun_df.iloc[:, 7]
val_dic = list(map(list, zip(mot_phon, patern_phon, n_syll, freqfilms2, freqlivres)))
lex3_dic =  { k:v for (k,v) in zip(mot_grapheme, val_dic)}


# ---------------------------------------------------------
# Fonctions
# ---------------------------------------------------------

def get_hyperval(lemma:str):
    """
    This fonction takes a lemma (str), look if that lemma is in wordnet dictionnary, 
    if it is, it returns the word hyperonym depth to the root of the dict (int)
    if not, it retunrs None
    
    parametre
    ------------
    :lemma: a lemma (str)
    :return: the lemma hyperonym value (int) or None

    exemple
    ------------
    >>> hyperval = get_hyperval('mouton')
    >>> expect : 7
    >>> hyperval = get_hyperval('birgb')
    >>> expect : None
    """
    synset = wordnet.synsets(lemma, None, 'fra', True)
    hyperscore = None
    meanhyper = None
    if len(synset) != 0:
        #for sens in synset:
            #print(sens)
        score_list = []
        for syn in synset:
            score_list.append(syn.min_depth())
        hyper1 = score_list[0]
        meanhyper = statistics.mean(score_list)
        modehyper = statistics.mode(score_list)



    return meanhyper

def get_sem_val(lemma:str,valence_dic,imagea_dic):
    """
    This fonction takes a lemma (str),
    and return a list containing the valence rating and imageability rating
    of that lemma
    
    parametre
    ------------
    :lemma: a lemma (str)
    :return: a list containnig two elements (str or None)

    exemple
    ------------
    >>> hyperval = get_hyperval('mouton')
    >>> expect : ["5.42", "84.400"]
    """
    valence = None
    imagea = None
    if lemma in valence_dic:
        valence = valence_dic[lemma]
    if lemma in imagea_dic:
        imagea = imagea_dic[lemma]
    return [valence,imagea]

def lex3_API_converter(lex_phon):
    tbl_lex = {'i': 'i', '3': 'ə', '°': '°', 'e': 'e', 'E': 'ɛ', 'A': 'a', 'a': 'a', 
     'o': 'o', 'O': 'ɔ', 'u': 'u', 'y': 'y', '2': 'ø', '9': 'œ', '@': 'ɑ̃', 
     '5': 'ɛ̃', '1': 'œ̃', '§': 'ɔ̃', 'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 
     'k': 'k', 'g': 'g', 'f': 'f', 'v': 'v', 's': 's', 'z': 'z', 'S': 'ʃ', 
     'Z': 'ʒ', 'm': 'm', 'n': 'n', 'N': 'ɲ', 'G': 'ŋ', 'l': 'l', 'R': 'ʁ', 
     'j': 'j', 'w': 'w', '8': 'ɥ'}
    

    api_phon = ''
    for caractere in lex_phon:
        if caractere in tbl_lex:
            api_phon = api_phon + tbl_lex[caractere]
        else:
            print('Caractère non reconnu : ',caractere)
    
    
    return api_phon

def get_phonetic(token:str,lex3_dic):
    """
    This fonction takes a token grapheme (ex: phonétique)
    return's it's phonetic form (ex: 'fɔnetik')
    it's phonologic pattern with syllabation (ex: 'CV.CV.CVC')
    and the number of syllable (ex: 3)

    parametre
    ------------
    :token: a graphem form (utf-8 str) 
    :return: a list containing 2 str and an int 
    or None if the token is not in the Dico
    (ex :)['fɔnetik', 'CV.CV.CVC', 3]
    """
    
    fonetik = None
    fonetik2 = None
    CVCV = None
    nsyll = None
    if token in lex3_dic:
        fonetik = lex3_dic[token][0]
        fonetik2 = lex3_API_converter(fonetik)
        CVCV = lex3_dic[token][1]
        nsyll = lex3_dic[token][2]
    
    all_phon = [fonetik2,CVCV,nsyll]
    return all_phon


def get_freq(lemma:str,lex3_dic,dictionnaire_other):
    """
    This fonction takes a token grapheme (ex: maman)
    return's it's lex3 corpus frequency for book and film

    parametre
    ------------
    :token: a graphem form (utf-8 str) 
    :return: a list containing 3 float 
    or 0 if the token is not in the Dico
    (ex : maman -> [10.12,2.43,0.1])
    """
    freq_film = 0
    freq_livre = 0
    freq_other = 0
    if lemma in lex3_dic:
        freq_film = lex3_dic[lemma][3]
        freq_livre = lex3_dic[lemma][4]
    if lemma in dictionnaire_other:
        freq_other = dictionnaire_other[lemma]
    all_freq = [freq_film,freq_livre,freq_other]
    return all_freq

# ---------------------------------------------------------
# 2 main loop
# ---------------------------------------------------------


''' 
canvas of the df DataFrame columns :
df_structure : {'id','collection_id','transcript_id','corpus_name','utterance_order',
                'speaker_role','speaker_name','gloss','target_child_age','token',
                'lemme', 'POS', 'n_token'}
'''

occ_match = {'nb_token' : 0, 'nb_nom' : 0, 'lex3' : 0, 'nb_UNK' : 0, 'valence' : 0, 'imagea' : 0, 'hyper' : 0}
n_child_token = 0
n_other_token = 0
dictionnaire = {}
dictionnaire_other = {}

id_list,phrase,tok,lemm,n_tok,POSTAGS,hyper,val,imag,phon,patterns,n_syllable,fq_livre,fq_film,fq_other,age = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]

stopword = ['xxx','x', 'xx', 'www' , 'yyy' , 'zzz','-', 'qqq',
            'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','ə','ɛ','ø']
interstopword = ['mm','oh','hum','hm','mmh','ouais','oui','ii',
                 'ah','ha','merci','non','bah','bouh','hue','là','ouh','hi','pan','euh','boum', 
                 'boom', 'ouah','nan','mh','okay','um','meuh','hou', 'oup','béh', 'wow', 'vrum', 
                 'ouf', 'eum', 'ola', 'mhm', 'na', 'hoplà', 'ei', 'tin', 'grr', 'pch', 'hu', 'wha', 
                 'hé', 'no', 'allö', 'pe', 'li', 'co', 'ci', 'wouh']

# making word frequency list for other overheard speech

print('---------------------------------------------------------')
print('Calculating word frequency per millon of overheard speech')
print('---------------------------------------------------------')

n_other_token = 0
for index, row in tqdm(df_other.iloc[:].iterrows(),total=df_other.shape[0]):
    uter = str(row['utterance'])
    id = str(row['id'])
    lemsents = ast.literal_eval(row['lemme'])
    POSTAG = ast.literal_eval(row['POS'])
    for idx, token in enumerate(lemsents): #iterate over all word in tokenized sentence
        n_other_token += 1
        lemme = str(lemsents[idx]).lower()
        POS = str(POSTAG[idx])
        ''' # filtering the stopword (codeword, onomatope and interjection)
        if POS == 'NOUN' and (token not in lex3_dic): # check if noun is in lexique382
                #lemme = token
                #POS = 'UNK'
        '''
        # making a Noun dictionnary_other and counting occurrence
        if POS[0] == 'n': 
            if lemme not in dictionnaire_other:
                dictionnaire_other[lemme] = 1
            else:
                dictionnaire_other[lemme] += 1

# calculating per million frequency of the overheard speech

for word in dictionnaire_other:
    #dictionnaire_other[word] = math.log10(dictionnaire_other[word]/n_other_token)
    dictionnaire_other[word] = (dictionnaire_other[word]/n_other_token)*1000000


sorteddictionairy_other = dict(reversed(sorted(dictionnaire_other.items(), key=lambda item: item[1])))
nom_other = sorteddictionairy_other.keys()
nb_occu_other = sorteddictionairy_other.values()
dico_other_final = {'Lemme' : nom_other, "Nombre d'occurence" : nb_occu_other}
overheard_dico = pd.DataFrame(dico_other_final)

print('---------------------------------------------------------')
print('Annotating hyperonymy, valence, imageability, phonetic, pattern ')
print('counting the occurence of each lemma in a dic')
print('and counting the quantity of dico match (raw_lemme vs valence vs imagea vs hyper vs phon)')
print('---------------------------------------------------------')

# making the main loop on target_child sentence

for index, row in tqdm(df.iloc[:].iterrows(),total=df.shape[0]): 
    uter = str(row['utterance'])
    id = str(row['id'])
    lemsents = ast.literal_eval(row['lemme'])
    POSTAG = ast.literal_eval(row['POS'])
    n_token = int(row['n_token'])
    child_age = row['age']
    for idx, lemme in enumerate(lemsents): #iterate over all word in tokenized sentence
        n_child_token += 1
        lemme = str(lemsents[idx]).lower()
        POS = str(POSTAG[idx])
        ''' # filtering the stopword (codeword, onomatope and interjection)
        if token in interstopword:
            lemme = token
            POS = 'INTJ'
        if POS == 'NOUN' and (token not in lex3_dic): # check if noun is in lexique382
                #lemme = token
                #POS = 'UNK'
        '''
        # get all the values (with custum fonction) for each NOUN
        if POS[0] == 'n' and POS != 'neg' and POS != 'n:prop':
            hyperscore = get_hyperval(lemme)
            sem_score = get_sem_val(lemme,valence_dic,imagea_dic)
            valence = sem_score[0]
            imageabilite = sem_score[1]
            phone_val = get_phonetic(lemme,lex3_dic)
            phonetic = phone_val[0]
            phono_pattern = phone_val[1]
            n_syll = phone_val[2]
            freq_val = get_freq(lemme,lex3_dic,dictionnaire_other)
            film = freq_val[0]
            livre = freq_val[1]
            other = freq_val[2]

            id_list.append(id)
            phrase.append(uter)
            tok.append(token)
            lemm.append(lemme)
            POSTAGS.append(POS)
            n_tok.append(n_token)
            hyper.append(hyperscore)
            val.append(valence)
            imag.append(imageabilite)
            phon.append(phonetic)
            patterns.append(phono_pattern)
            n_syllable.append(n_syll)
            fq_film.append(film)
            fq_livre.append(livre)
            fq_other.append(other)
            age.append(child_age)
        #calculate the matching score for Dict
        occ_match['nb_token'] += 1 #count number of token
        if POS[0] == 'n' and POS != 'neg' and POS != 'n:prop' and  (lemme in lex3_dic):
            occ_match['nb_nom'] += 1
            if hyperscore != None:
                occ_match['hyper'] += 1
            if valence != None:
                occ_match['valence'] += 1
            if imageabilite != None:
                occ_match['imagea'] += 1
            if lemme in lex3_dic:
                occ_match['lex3'] += 1
            else:
                occ_match['nb_UNK'] += 1
        # making a Noun dictionnary and counting occurrence
        if POS[0] == 'n' and POS != 'neg' and POS != 'n:prop' and  (lemme in lex3_dic): 
            if lemme not in dictionnaire:
                dictionnaire[lemme] = 1
            else:
                dictionnaire[lemme] += 1

# making the result into 2 Dict ready to be converted to Dataframe
sorteddictionairy = dict(reversed(sorted(dictionnaire.items(), key=lambda item: item[1])))
nom = sorteddictionairy.keys()
nb_occu = sorteddictionairy.values()
taille_voca = str(len(nom))

dico_final = {'Lemme' : nom, "Nombre d'occurence" : nb_occu}

donne_final = {'id': id_list, 'occurence': phrase, 'lemma': lemm,'POS': POSTAGS,
                'score_hyper': hyper, 'score_valance': val, 'score_imagea': imag, 
                'phonetic': phon,'pattern': patterns, 'freq_lem_film' : fq_film, 'freq_lem_livre' : fq_livre, 'freq_overheard' : fq_other, 'age': age}


#make resulting Dict to DataFrame
data_dico_final = pd.DataFrame(dico_final)
datafinal = pd.DataFrame(donne_final)

type_match = {'CLAN': [], 'lex3': [], 'fan': [], 'semQc': [], 'wordnet': []}

# getting the matching word for dico
for noun in dictionnaire:
    type_match['CLAN'].append(noun)
    if noun in lex3_dic:
        type_match['lex3'].append(noun)
    if noun in valence_dic:
        type_match['fan'].append(noun)
    if noun in imagea_dic:
        type_match['semQc'].append(noun)
    synset = wordnet.synsets(noun, None, 'fra', True)
    if len(synset) != 0:
        type_match['wordnet'].append(noun)

nb_type_match = {}
for dicos in type_match:
    nb_type_match[dicos] = len(type_match[dicos])

print('---------------------------------------------------------')
print('Loop done. Printing and saving results')
print('---------------------------------------------------------')

print(datafinal)
print(occ_match)
print(nb_type_match)
print('Taille du vocab : ', taille_voca)

#saving the result
datafinal.to_csv('annotated_french_corpa.csv', sep = '\t', encoding='utf-8')
data_dico_final.to_csv('analyse_dico.csv', sep = '\t', encoding='utf-8')

donne_descriptive = open('donne_descriptive.txt', "w")
donne_descriptive.write('Filtre : '+filtre+'\n'+'Taille du vocabulaire : '+taille_voca+'\n'+str(occ_match)+'\n'+str(nb_type_match)+'\n'+'corpus : '+str(all_corpus))
donne_descriptive.close()

print('---------------------------------------------------------')
print('Saving Successful')
print('---------------------------------------------------------')
