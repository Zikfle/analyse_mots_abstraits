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
from module.tee_logger import start_capture, get_log, save_string_to_file

import time

start_capture() # to save console print to log

doc_path = '/Users/zikfle/Documents/Maitrise-analyse'
parsed_file_name = 'french_corpa_parsed.csv'
tokenized_file_name = 'french_corpa_token.csv'
annotated_file_name = 'french_corpa_annotated.csv'
child_dico_name = 'child_dico.csv'
over_dico_name = 'over_dico.csv'

data_folder_location = os.path.join(doc_path,'data')
raw_data_folder_location = os.path.join(doc_path,'data/French-Corpa')
result_folder_location = os.path.join(doc_path,'results')

parsed_path = os.path.join(doc_path,'results',parsed_file_name)
token_path = os.path.join(doc_path,'results',tokenized_file_name)

parsing = True
tokenization = True
annotation = True
name_of_version = 'version 3'

start_time = time.perf_counter()

if parsing == True:
    parsed_data = parser.parse_chat_folder(raw_data_folder_location)
    parsed_path = ctm_saver.safe_save(parsed_data,result_folder_location,parsed_file_name, sep = ",",index=True)

if tokenization == True:
    token_data = tokenizer.parse_token(parsed_path)
    token_path = ctm_saver.safe_save(token_data,result_folder_location,tokenized_file_name,index=True)

if annotation == True:
    datafinal, data_dico_final, overheard_dico, param = annotator.annotating(data_folder_location,token_path)
    annotated_path = ctm_saver.safe_save(datafinal,result_folder_location,annotated_file_name, sep = ",")
    child_dico_path = ctm_saver.safe_save(data_dico_final,result_folder_location,child_dico_name, sep = ",")
    over_dico_path = ctm_saver.safe_save(overheard_dico,result_folder_location,over_dico_name, sep = ",")
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.1f} seconds")
    log_contents = get_log()
    log = f"####################\n{name_of_version}\n####################\n\nparam\n"
    log = log + log_contents
    save_string_to_file(os.path.join(result_folder_location,f"log{name_of_version}.txt"), log)

    print('---------------------------------------------------------')
    print('Done')
    print('---------------------------------------------------------')