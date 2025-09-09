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


nlp = spacy.load("fr_core_news_md")

df = pd.read_csv('Data - corpus_french.csv')

#print(df.head(3))

df2 = df[['Unnamed: 0', 'id', 'gloss', 'stem', 'actual_phonology',
       'model_phonology', 'type', 'language', 'num_morphemes', 'num_tokens',
       'utterance_order', 'corpus_name', 'part_of_speech', 'speaker_code',
       'speaker_name', 'speaker_role', 'target_child_name', 'target_child_age',
       'target_child_sex', 'media_start', 'media_end', 'media_unit',
       'collection_name', 'collection_id', 'corpus_id', 'speaker_id',
       'target_child_id', 'transcript_id']]



#print(df.columns)

nb_token = df['num_tokens'].sum()

all_participant = df['speaker_name']
all_uttrances = df['gloss']

registre = []

for participant in all_participant:
    if participant not in registre:
        registre.append(participant)

#print(registre)
#print(len(registre))
count = 0
fstrow = []
for row in df.iterrows():
    count += 1
    if count > 40740:
        fstrow.append(row)
        break

print(fstrow)





