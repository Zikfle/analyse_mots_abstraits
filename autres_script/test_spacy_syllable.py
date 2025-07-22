# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-02-22
# Description: testing the spacy syllable module
# MIT License
# ---------------------------------------------------------

### Importing strandard library
import os
#import re
#import pickle
#import json 
from tqdm import tqdm
import pandas as pd
import ast #for reading string as list

### Importing nlp library
import spacy
from spacy_syllables import SpacySyllables
#import nltk
#nltk.download('omw-1.4')
#from nltk.corpus import wordnet

# setting up cuda gpu for spacy
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#spacy.require_gpu()
#torch.cuda.set_per_process_memory_fraction(0.9, device=0) # limiting python gpu memory usage to 90%
#nlp = spacy.load("fr_dep_news_trf",disable=['parser']) # importing spacy model: french_transformer

nlp = spacy.load("fr_core_news_sm",disable=['parser']) # importing spacy model: french_small
nlp.add_pipe("syllables")



# ---------------------------------------------------------
# Fonctions
# ---------------------------------------------------------

def get_syllable(token:str):
    """
    This fonction takes a token (str) segment it in syllable
    and return a list of syllabe and a the nb. of syllable (int)
    paramt
    :token: a token as string
    :return: a list containning two elements :
        [0] a list of string (containing the segmented syllable)
        [1] a int that's a count of syllable
    exemple
    ------------
    >>> life = get_syllable('mouton')
    >>> expect : [['mou', 'ton'], 2]
    """
    syll_token = nlp(token)
    for word in syll_token:
        syllables = [word._.syllables, word._.syllables_count]
    
    return syllables

# ---------------------------------------------------------
# Main loop
# ---------------------------------------------------------

test = ['chien','mouton','amérique','table','main','désertification']

for list_mot in tqdm(test):
    les_mots = ast.literal_eval(list_mot)
    for mot in les_mots:
        syllabes = get_syllable(mot)
        print(mot)
        print(syllabes)


