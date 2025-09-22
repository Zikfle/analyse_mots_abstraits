# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-09-09
# Description: Main script of the project to run the different step of the analysis.
# MIT License
# ---------------------------------------------------------

import os

import module.childes_parser as parser
import module.tokenisation as tokenizer
import module.annotator as annotator

import module.custom_panda_saver as ctm_saver

def save_string_to_file(path, string):
    try:
        # Check if the path is a file or not
        if os.path.isfile(path):
            with open(path, 'a') as file:
                file.write(string + '\n')
        else:
            # If it's not a file, create one and add the string
            with open(path, 'w+') as file:
                file.write(string + '\n')

    except Exception as e:
        print(f"An error occurred: {e}")

data_folder_location = '/Users/zikfle/Documents/Maitrise-analyse/data'
raw_data_folder_location = '/Users/zikfle/Documents/Maitrise-analyse/data/French-Corpa'
result_folder_location = '/Users/zikfle/Documents/Maitrise-analyse/results'

parsed_path = '/Users/zikfle/Documents/Maitrise-analyse/results/french_corpa_parsed1.tsv'
token_path = '/Users/zikfle/Documents/Maitrise-analyse/results/french_corpa_token1.tsv'

parsing = True
tokenization = True
annotation = True
name_of_version = 'Version 1'

if parsing == True:
    parsed_data = parser.parse_chat_folder(raw_data_folder_location)
    parsed_path = ctm_saver.safe_save(parsed_data,result_folder_location,'french_corpa_parsed1.tsv',index=True)

if tokenization == True:
    token_data = tokenizer.parse_token(parsed_path)
    token_path = ctm_saver.safe_save(token_data,result_folder_location,'french_corpa_token1.tsv',index=True)

if annotation == True:
    datafinal, data_dico_final, overheard_dico, param = annotator.annotating(data_folder_location,token_path)
    annotated_path = ctm_saver.safe_save(datafinal,result_folder_location,'french_corpa_annotated1.tsv')
    child_dico_path = ctm_saver.safe_save(data_dico_final,result_folder_location,'child_dico1.tsv')
    over_dico_path = ctm_saver.safe_save(overheard_dico,result_folder_location,'over_dico1.tsv')
    log = f'####################\n{name_of_version}\n####################\n\nparam\n'''
    save_string_to_file(os.path.join(result_folder_location,'log.txt'), log)