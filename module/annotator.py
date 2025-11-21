# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-01-28
# Description:  Automatic annotation of data from corpus French Corpa CHILDES
#               Annotation automatique des données du corpus French Corpa CHILDES
# MIT License
# ---------------------------------------------------------

### Importing standard library
import os #for file management
#import re
#import pickle
#import json 
from tqdm import tqdm #for progress bar
import pandas as pd #for dataframe management
import math
import ast #for reading string as list
import unicodedata #for reading string as unicode

### Importing nlp library
import nltk #for using Wordnet
nltk.download('omw-1.4') #making sure Wordnet is installed
from nltk.corpus import wordnet
import statistics
from collections import Counter

# ---------------------------------------------------------
# Fonctions
# ---------------------------------------------------------

def get_hyperval(lemma:str):
    """
    This fonction takes a lemma (str), look if that lemma is in wordnet dictionnary, 
    if it is, it returns the word hyperonym depth to the root of the dict (int)
    if not, it return None
    
    parametre
    ------------
    lemma: a lemma (str)
    return: the lemma hyperonym value (int) or None

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
    
    parameter
    ------------
    lemma: a lemma (str)
    return: a list containing two elements (str or None)

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
    tbl_lex = {
    'i': 'i', '3': 'ə', '°': '°', 'e': 'e', 'E': 'ɛ', 'A': 'a', 'a': 'a', 
    'o': 'o', 'O': 'ɔ', 'u': 'u', 'y': 'y', '2': 'ø', '9': 'œ', '@': 'ɑ̃', 
    '5': 'ɛ̃', '1': 'œ̃', '§': 'ɔ̃', 'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 
    'k': 'k', 'g': 'g', 'f': 'f', 'v': 'v', 's': 's', 'z': 'z', 'S': 'ʃ', 
    'Z': 'ʒ', 'm': 'm', 'n': 'n', 'N': 'ɲ', 'G': 'ŋ', 'l': 'l', 'R': 'ʁ', 
    'j': 'j', 'w': 'w', '8': 'ɥ'
     }
    

    api_phon = ''
    for character in lex_phon:
        if character in tbl_lex:
            api_phon = api_phon + tbl_lex[character]
        else:
            print('Caractère non reconnu : ',character)
    
    
    return api_phon

def get_phonetic(token:str,lex3_dic):
    """
    This fonction takes a token grapheme (ex: phonétique)
    return's it's phonetic form (ex: 'fɔnetik')
    it's phonologic pattern with syllabation (ex: 'CV.CV.CVC')
    and the number of syllable (ex: 3)

    parameter
    ------------
    :token: a grapheme form (utf-8 str) 
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


def get_freq(lemma:str,lex3_dic,dictionary_other):
    """
    This fonction takes a token grapheme (ex: maman)
    return's it's lex3 corpus frequency for book and film

    parameter
    ------------
    :token: a grapheme form (utf-8 str) 
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
    if lemma in dictionary_other:
        freq_other = dictionary_other[lemma]
    all_freq = [freq_film,freq_livre,freq_other]
    return all_freq

def hdd(text):
	#requires Counter import
	def choose(n, k): #calculate binomial
		"""
		A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
		"""
		if 0 <= k <= n:
			ntok = 1
			ktok = 1
			for t in range(1, min(k, n - k) + 1): #this was changed to "range" from "xrange" for py3
				ntok *= n
				ktok *= t
				n -= 1
			return ntok // ktok
		else:
			return 0

	def hyper(successes, sample_size, population_size, freq): #calculate hypergeometric distribution
		#probability a word will occur at least once in a sample of a particular size
		try:
			prob_1 = 1.0 - (float((choose(freq, successes) * choose((population_size - freq),(sample_size - successes)))) / float(choose(population_size, sample_size)))
			prob_1 = prob_1 * (1/sample_size)
		except ZeroDivisionError:
			prob_1 = 0
			
		return prob_1

	prob_sum = 0.0
	ntokens = len(text)
	types_list = list(set(text))
	frequency_dict = Counter(text)

	for items in types_list:
		prob = hyper(0,42,ntokens,frequency_dict[items]) #random sample is 42 items in length
		prob_sum += prob

	return prob_sum


def annotating(data_path,token_path):
    """
    Main annotation process
    """

    # ---------------------------------------------------------
    # Data management
    # ---------------------------------------------------------

    #import the main corpus datafile
    df = pd.read_csv(token_path, sep = ',', encoding='utf-8')
    print(df.columns)
    print(df)
    #create a list of all speaker_role
    all_role = df['role'].unique()
    #print(all_role)

    '''
    all_role = ['Target_Child', 'Mother', 'Brother', 'Father', 'Sister', 'Visitor', 'Relative',
    'Investigator', 'Unidentified', 'Boy', 'Caretaker', 'Teenager', 'Grandmother',
    'Child', 'Adult', 'Grandfather', 'Girl', 'Media', 'Playmate', 'Teacher',       
    'Friend', 'Student']
    '''

    #filter the data - keep overheard speech
    other_role = ['Mother', 'Brother', 'Father', 'Sister', 'Visitor', 'Relative',
    'Investigator', 'Unidentified', 'Boy', 'Caretaker', 'Teenager', 'Grandmother',
    'Adult', 'Grandfather', 'Girl', 'Media', 'Playmate', 'Teacher',       
    'Friend', 'Student'] # removing child and target_child

    df_other = df[df['role'].isin(other_role)]

    #filter the data - keep target child
    filter = "df = df.loc[df['role'] == ('Target_Child')]"
    df = df.loc[df['role'] == ('Target_Child')]


    all_corpus = sorted(df['corpus'].unique())
    print(f"Corpus included : {all_corpus}")

    #import valence data into a dictionary
    valence_df = pd.read_csv(os.path.join(data_path, "data_fan_valence.csv"))
    mot_fan = valence_df.iloc[:, 0]
    mot_valence = valence_df.iloc[:, 4]
    valence_dic = dict(zip(mot_fan[1:], mot_valence[1:]))

    #import imageability data into a dictionary
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

    ''' 
    canvas of the df DataFrame columns :
    df_structure : {'id','collection_id','transcript_id','corpus_name','utterance_order',
                    'speaker_role','speaker_name','gloss','target_child_age','token',
                    'lemme', 'POS', 'n_token'}
    '''

    occ_match = {'nb_token' : 0, 'nb_nom' : 0, 'lex3' : 0, 'nb_UNK' : 0, 'valence' : 0, 'imagea' : 0, 'hyper' : 0}
    n_child_token = 0
    n_other_token = 0
    dictionary = {}
    dictionary_other = {}

    id_list,participant_ids,participant_names,sentence,tok,lemm,n_tok,POSTAGS,hyper,val,imag,phon,patterns,n_syllable,fq_livre,fq_film,fq_other,mlus,vocds,age = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]

    stopword = ['xxx','x', 'xx', 'www' , 'yyy' , 'zzz','-', 'qqq',
                'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','ə','ɛ','ø']
    interstopword = ['mm','oh','hum','hm','mmh','ouais','oui','ii',
                    'ah','ha','merci','non','bah','bouh','hue','là','ouh','hi','pan','euh','boum', 
                    'boom', 'ouah','nan','mh','okay','um','meuh','hou', 'oup','béh', 'wow', 'vrum', 
                    'ouf', 'eum', 'ola', 'mhm', 'na', 'hoplà', 'ei', 'tin', 'grr', 'pch', 'hu', 'wha', 
                    'hé', 'no', 'allö', 'pe', 'li', 'co', 'ci', 'wouh']

    # making word frequency list for other overheard speech

    print('----------------------------------------------------------')
    print('Calculating word frequency per million of overheard speech')
    print('----------------------------------------------------------')

    n_other_token = 0
    for index, row in tqdm(df_other.iloc[:].iterrows(),total=df_other.shape[0],desc='Overheard speech'):
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
            # making a Noun dictionary_other and counting occurrence
            if POS[0] == 'n': 
                if lemme not in dictionary_other:
                    dictionary_other[lemme] = 1
                else:
                    dictionary_other[lemme] += 1

    # calculating per million frequency of the overheard speech
    dictionary_other = {word: (nb / n_other_token) * 1000000 for word, nb in dictionary_other.items()}


    sorted_dictionary_other = dict(reversed(sorted(dictionary_other.items(), key=lambda item: item[1])))
    nom_other = sorted_dictionary_other.keys()
    nb_occu_other = sorted_dictionary_other.values()
    dico_other_final = {'Lemme' : nom_other, "Number of occurrence" : nb_occu_other}
    overheard_dico = pd.DataFrame(dico_other_final)

    print('---------------------------------------------------------')
    print('Calculating mlu and VocD per participant')
    print('---------------------------------------------------------')

    mlu_dict = df.groupby(['participant_id', 'transcript_id'])['n_token'].mean().to_dict()
    #print(mlu_dict)
    
    vocd_dict = {}

    individual_case = {}
    for key in tqdm(mlu_dict.keys(),desc='Collating each individual case as bags of words '): # iterrate over individual case
        subset = df[(df['participant_id'] == key[0]) & (df['transcript_id'] == key[1])]
        transcript_lemma = subset['lemme'].tolist()
        transcript_pos = subset['POS'].tolist()
        individual_case[key] = []
        for lemma_list, pos_list in zip(transcript_lemma,transcript_pos): # iterrate over each lemmatized individual case
            lemma_list = ast.literal_eval(lemma_list)
            pos_list = ast.literal_eval(pos_list)
            for lemma,pos in zip(lemma_list,pos_list):
                if pos != 'X' and pos != 'cm':
                    individual_case[key].append(lemma) # collate each lemma in a list for each individual case

    for key, value in tqdm(individual_case.items(),desc='Computing hdd for each individual case'):
        #print(key)
        #print(len(value))
        if len(value) < 50:
            vocd_dict[key] = None
        else:
            vocd = hdd(value)
            vocd_dict[key] = vocd
        
    print('---------------------------------------------------------')
    print('Annotating hyperonymy, valence, imageability, phonetic, pattern')
    print('counting the occurrence of each lemma in a dic')
    print('and counting the quantity of dico match (raw_lemme vs valence vs imagea vs hyper vs phon)')
    print('---------------------------------------------------------')

    # making the main loop on target_child sentence

    for index, row in tqdm(df.iloc[:].iterrows(),total=df.shape[0],desc='Main loop annotating word value'): 
        uter = str(row['utterance'])
        id = str(row['id'])
        transcript_id = str(row['transcript_id'])
        participant_id = str(row['participant_id'])
        participant_name = str(row['participant_name'])
        lemsents = ast.literal_eval(row['lemme'])
        POSTAG = ast.literal_eval(row['POS'])
        n_token = int(row['n_token'])
        child_age = row['age']
        mlu = mlu_dict[(float(participant_id), float(transcript_id))]
        vocd = vocd_dict[(float(participant_id), float(transcript_id))]
        for idx, lemme in enumerate(lemsents): #iterate over all word in tokenized sentence
            n_child_token += 1
            lemme = str(lemsents[idx]).lower()
            POS = str(POSTAG[idx])
            ''' # filtering the stopword (codeword, onomatopoeia and interjection)
            if token in interstopword:
                lemme = token
                POS = 'INTJ'
            if POS == 'NOUN' and (token not in lex3_dic): # check if noun is in lexique382
                    #lemme = token
                    #POS = 'UNK'
            '''

            # get all the values (with custom function) for each NOUN
            if POS[0] == 'n' and POS != 'neg' and POS != 'n:prop':
                hyperscore = get_hyperval(lemme)
                sem_score = get_sem_val(lemme,valence_dic,imagea_dic)
                valence = sem_score[0]
                imageabilite = sem_score[1]
                phone_val = get_phonetic(lemme,lex3_dic)
                phonetic = phone_val[0]
                phono_pattern = phone_val[1]
                n_syll = phone_val[2]
                freq_val = get_freq(lemme,lex3_dic,dictionary_other)
                film = freq_val[0]
                livre = freq_val[1]
                other = freq_val[2]

                id_list.append(id)
                participant_ids.append(participant_id)
                participant_names.append(participant_name)
                sentence.append(uter)
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
                mlus.append(mlu)
                vocds.append(vocd)
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
                if lemme not in dictionary:
                    dictionary[lemme] = 1
                else:
                    dictionary[lemme] += 1
    # making Noun dict on a frequency over / million word
    dictionary = {lemme: (nb / n_child_token) * 1000000 for lemme, nb in dictionary.items()}
    # making the result into 2 Dict ready to be converted to Dataframe
    sorted_dictionary = dict(reversed(sorted(dictionary.items(), key=lambda item: item[1])))
    nom = sorted_dictionary.keys()
    nb_occu = sorted_dictionary.values()
    taille_voca = str(len(nom))

    dico_final = {'Lemme' : nom, "Number of occurrence" : nb_occu}

    donne_final = {'id': id_list, 'participant_id': participant_ids, 
                   'participant_name': participant_names,
                   'occurrence': sentence, 
                   'lemma': lemm,'POS': POSTAGS,
                    'score_hyper': hyper, 'score_valance': val, 'score_imagea': imag, 
                    'phonetic': phon,'pattern': patterns, 'freq_lem_film' : fq_film, 'freq_lem_livre' : fq_livre, 'freq_overheard' : fq_other,'mlu' : mlus,'HDD' : vocds, 'age': age}


    #make resulting Dict to DataFrame
    data_dico_final = pd.DataFrame(dico_final)
    datafinal = pd.DataFrame(donne_final)

    type_match = {'CLAN': [], 'lex3': [], 'fan': [], 'semQc': [], 'wordnet': []}

    # getting the matching word for dico
    for noun in dictionary:
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
    print('Loop done. Printing results and saving param')
    print('---------------------------------------------------------')

    print(datafinal)
    print(occ_match)
    print(nb_type_match)
    print('Taille du vocab : ', taille_voca)

    param = 'Filter : ' + filter +'\n'+'Taille du vocabulaire : '+taille_voca+'\n'+str(occ_match)+'\n'+str(nb_type_match)+'\n'+'corpus : '+str(all_corpus)

    return datafinal, data_dico_final, overheard_dico, param

# ---------------------------------------------------------
# Param
# ---------------------------------------------------------

run_as_test = False
saving = False
save_name = 'annotated_french_corpa1.csv'

if run_as_test == True:
    token_path = '/Users/zikfle/Documents/Maitrise-analyse/results/french_corpa_token1.csv'
    result_folder_location = '/Users/zikfle/Documents/Maitrise-analyse/results'
    data_folder_location = "/Users/zikfle/Documents/Maitrise-analyse/data"
    datafinal, data_dico_final, overheard_dico, param = annotating(data_folder_location,token_path)

    if saving == True:
        print('---------------------------------------------------------')
        print('Saving annotation results')
        print('---------------------------------------------------------')
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
                datafinal.to_csv(out_file, sep='\t', encoding='utf-8')
                print('-' * 50)
                print('Saving successful')
                print('-' * 50)
        else:
            datafinal.to_csv(out_file, sep='\t', encoding='utf-8')

            print('---------------------------------------------------------')
            print('Saving successful')
            print('---------------------------------------------------------')
        #saving overheard and child_dico
        data_dico_final.to_csv('child_dico1.tsv', sep = '\t', encoding='utf-8')
        overheard_dico.to_csv('over_dico1.tsv', sep = '\t', encoding='utf-8')


        print('---------------------------------------------------------')
        print('Saving param successful')
        print('---------------------------------------------------------')
    else:
        print('---------------------------------------------------------')
        print('Saving set to false')
        print('---------------------------------------------------------')
