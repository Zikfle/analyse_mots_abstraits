# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-04-13
# Description: CHILDES parser
# MIT License
# ---------------------------------------------------------

import os
import regex as re
from tqdm import tqdm
import pandas as pd
import statistics

def parse_metadata(transcript,filename,transcript_id):
    rawmetadata = []
    metadata = {'participants' : [] , 'IDS' : []}
    for line in transcript:
        if line[0] == '@':
            rawmetadata.append(line)
        if len(line) != 2:
            continue
        line_type = line[0]
        content = line[1]
        if line_type == '@Participants:':
            metadata['participants'] = content.split(',')
        if line_type == '@ID:':
            metadata['IDS'].append(content.split('|')) # sould always give a list with 10 element
    metadata2 = {'codeb' : [] , 'roleb' : [] , 'file_name' : [] , 'transcript_id' : [] , 'lang' : [] , 'corpus' : [] , 'code' : [] , 'age' : [] , 
                 'sex' : [] , 'group' : [] , 'SES' : [] , 'role' : [] , 'education' : [] , 'custom' : [], }
    for idx , participant in enumerate(metadata['participants']):
        #print(participant)
        participant = participant.split(' ')
        #print(participant)
        metadata2['codeb'].append(participant[-2])
        metadata2['roleb'].append(participant[-1])
        metadata2['file_name'].append(filename)
        metadata2['transcript_id'].append(transcript_id)
        metadata2['lang'].append(metadata['IDS'][idx][0])
        metadata2['corpus'].append(metadata['IDS'][idx][1])
        metadata2['code'].append(metadata['IDS'][idx][2])
        metadata2['age'].append(metadata['IDS'][idx][3])
        metadata2['sex'].append(metadata['IDS'][idx][4])
        metadata2['group'].append(metadata['IDS'][idx][5])
        metadata2['SES'].append(metadata['IDS'][idx][6])
        metadata2['role'].append(metadata['IDS'][idx][7])
        metadata2['education'].append(metadata['IDS'][idx][8])
        metadata2['custom'].append(metadata['IDS'][idx][9])
        
            
    return metadata2

def age_to_days(age):
    days = None
    if type(age) is str and age != '':
        year_month_day = age.split(';')
        year = int(year_month_day[0])
        month_day = year_month_day[1]
        if '.' in month_day:
            month_day = month_day.split('.')
            try:
                month = int(month_day[0])
            except:
                month = 0
            try:
                day = int(month_day[1])
            except:
                day = 0
        else: 
            month = 0
            day = 0
        days = (year * 365) + (month * 30.5) + day
    #else:
        #print('age : ',age)
    return days

def parse_lines(transcript,metadata,transcript_name):
    code = ''
    utterance = ''
    gra = ''
    mor = ''
    pho = ''
    act = ''
    sit = ''
    com = ''
    oldtype = '*'

    transcript_dict = {'transcript_name' : [],'transcript_id': [], 'corpus' : [], 'transcript_order': [], 'code': [],
                               'role': [],'age': [], 'target_age': [], 'utterance': [],'mor': [],'gra': [],'pho': [],'act': [],
                               'com': [],'sit': []}
    id_line = 1
    if 'Target_Child' in metadata['role']:
        targets = [i for i, x in enumerate(metadata['role']) if x == 'Target_Child']
        ages = []
        for target in targets:
            target_age = metadata['age'][target]
            target_age = age_to_days(target_age)
            if target_age != '':
                ages.append(target_age)
        try:
            target_age = statistics.mean(ages)
        except:
            target_age = None
    else:
        target_age = None
    for line in transcript:
        id_line += 1
        if len(line) != 2:
            continue
        type = line[0]
        content = line[1]
        if type == '':
            if oldtype == '*':
                utterance = utterance + ' ' + content
            if oldtype == '%gra:':
                gra = gra + ' ' + content
            if oldtype == '%mor:':
                mor = mor + ' ' + content
            if oldtype == '%pho:':
                pho = pho + ' ' + content
            if oldtype == '%act:':
                act = act + ' ' + content
            if oldtype == '%com:':
                com = com + ' ' + content
            if oldtype == '%sit:':
                sit = sit + ' ' + content
        else:
            if (type[0] == '*') and (len(utterance) > 1):
                for idx, codeb in enumerate(metadata['code']):
                    if codeb == code:
                        position = idx
                        #print(metadata['transcript_id'])
                        #print(position)
                        transcript_id = metadata['transcript_id'][position]
                        role = metadata['role'][position]
                        age = metadata['age'][position]
                        age = age_to_days(age)
                        corpus = metadata['corpus'][position]
                        continue

                transcript_dict['transcript_name'].append(transcript_name)
                transcript_dict['transcript_id'].append(transcript_id)
                transcript_dict['corpus'].append(corpus)
                transcript_dict['transcript_order'].append(id_line)
                transcript_dict['code'].append(code)
                transcript_dict['role'].append(role)
                transcript_dict['age'].append(age)
                transcript_dict['target_age'].append(target_age)
                transcript_dict['utterance'].append(utterance)
                transcript_dict['mor'].append(mor)
                transcript_dict['gra'].append(gra)
                transcript_dict['pho'].append(pho)
                transcript_dict['act'].append(act)
                transcript_dict['com'].append(com)
                transcript_dict['sit'].append(sit)
                
                age = ''
                code = ''
                utterance = ''
                gra = ''
                mor = ''
                pho = ''
                act = ''
                sit = ''
                com = ''
                oldtype = '*'

            if type[0] == '*':
                utterance = content
                code = type[1:-1]
            if type == '%gra:':
                gra = content
            if type == '%mor:':
                mor = content
            if type == '%pho:':
                pho = content
            if type == '%act:':
                act = content
            if type == '%com:':
                com = content
            if type == '%sit:':
                sit = content
            oldtype = type

    transcript_df = pd.DataFrame(transcript_dict)
    return transcript_df


def parse_chat_folder(data_path):

    print('-----------------------------------------------------------')
    print(f'Reading all the cha. files in {data_path} and saving it into a Python Dict')
    print('-----------------------------------------------------------')

    transcript_save = {}

    filelist = os.listdir(data_path)
    filelist.sort()
    print('Nb. of files : ',len(filelist))
    for file in tqdm(filelist[:]):
        if file.endswith(".cha"):
            transcript = open(os.path.join(data_path,file),'r',encoding = 'utf-8')
            transcript_lines = transcript.readlines()
            transcript_as_list = []
            for idx, line in enumerate(transcript_lines):
                line = line.split('\t')
                if len(line) == 2:
                    line[1] = re.sub('\x15.*\x15','',line[1])
                    line[1] = re.sub('\n','',line[1])
                transcript_as_list.append(line)
            transcript_save[file] = transcript_as_list

    #print(transcript_save)

    corpus,transcript_id,transcript_file,name_participant,role,age,abreviation,utterance,mor,gra,act,com,sit,other = [],[],[],[],[],[],[],[],[],[],[],[],[],[]
    transcript_id = 0
    all_dfs = []

    print('---------------------------------------------------------')
    print('Parsing each .cha file into a DataFrame')
    print('---------------------------------------------------------')

    for transcript_name in tqdm(transcript_save.keys()):
        transcript_id += 1
        transcript = transcript_save[transcript_name]
        metadata = parse_metadata(transcript,transcript_name,transcript_id)
        parsed_transcript = parse_lines(transcript,metadata,transcript_name)
        all_dfs.append(parsed_transcript)

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.index.name = 'id'
    print(final_df)
    
    return final_df

# ---------------------------------------------------------
# Param
# ---------------------------------------------------------

run_as_test = False
saving = False
save_name = 'french_corpa_parsed1.tsv'

# run main function
if run_as_test == True:
    data_folder_location = 'A://Maitrise-analyse/data/French-Corpa'
    result_folder_location = 'A://Maitrise-analyse/results'

    final_df = parse_chat_folder(data_folder_location)

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
                final_df.to_csv(out_file, sep='\t', encoding='utf-8')
                print('-' * 50)
                print('Saving successful')
                print('-' * 50)
        else:
            final_df.to_csv(out_file, sep='\t', encoding='utf-8')

            print('---------------------------------------------------------')
            print('Saving successful')
            print('---------------------------------------------------------')
    
    else:
        print('---------------------------------------------------------')
        print('Saving set to false')
        print('---------------------------------------------------------')
    
