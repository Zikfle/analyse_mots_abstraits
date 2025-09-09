# analyse_mots_abstraits

<style>body {text-align: justify}</style>

# Master Memoir Project – Data Analysis  
**Child Acquisition of Abstract Nouns**  

> *“Studying how children learn abstract nouns such as *democracy*, *liberty*, *freedom* and other conceptual words.”*

This repository contains the data‑analysis portion of the master’s memoir project. It processes the [FrenchCorpa](https://talkbank.org/childes/access/French/) dataset from [CHILDES](https://talkbank.org/childes/) to annotate the instance of noun in child speech where I extract the tokenisation and part‑of‑speech tags form CLAN analysis. I then produce an annotation tsv file that marks all detected nouns with it's associated annotation with various method (lemma, POS, hyperonymy,valance ,imageability ,phonetic form, phonetic pattern, frequency from previous data, frequency in overheard speech, age).

## Table of Contents

| Section | Description |
|---------|-------------|
| [Project Overview](#project-overview) | What the project is about. |
| [Data](#data) | Source, format, and privacy notes. |
| [Repository Structure](#repository-structure) | How the files are organised. |
| [Setup](#setup) | Installing dependencies. |
| [Usage](#usage) | Running the pipeline. |
| [Output](#output) | What you’ll get. |
| [Results & Analysis](#results-analysis) | How the output is used. |
| [Future Work](#future-work) | Ideas for extending the project. |
| [License](#license) | Legal information. |
| [Contact](#contact) | Who to reach out to. |

---

## Project Overview

The core research question is: **How do children acquire and abstract nouns?**  
Abstract nouns are concepts that cannot be directly perceived by the senses (e.g., *freedom*, *love*, *justice*).  
Our dataset contains child‑spoken transcripts annotated by linguistic experts.  

The **data‑analysis** part of the project does three things:
1. **Parse the preprocessed dataset in a large .tsv file** – read all the .cha preprocessed .cha file in a folder and save the data into a .tsv file where each lines is an utterance with all it's metadata (role, age ...) in a raw fasion.
2. **Extract Tokenisation & POS‑tagging from CLAN** – read the .tsv dataset and parse the %mor information into different column (lemma,POS,flexion).
3. **Annotate the nouns** – read all the lines and create a new .tsv dataset where each line is a flagged noun and associate to that noun (from it's lemma) the relevant variable value (hyperonymy, valance, imageability...)


**Table 1 – Overview of the variables studied in the memoir**

| Factor category               | Variable                               | Variable type          |
|-------------------------------|----------------------------------------|------------------------|
| **Independent factor**        | Age of noun appearance                 | Continuous numeric     |
| **Lexical‑specific factors**  | Word length                            | Discrete numeric       |
|                               | Phonetic pattern                       | Nominal                |
|                               | Valence                                | Continuous numeric     |
|                               | Degree of imageability                 | Continuous numeric     |
|                               | Hypernym score                         | Discrete numeric       |
| **Input‑related factors**     | Global word frequency                  | Continuous numeric     |
|                               | Frequency per session                  | Continuous numeric     |
|                               | Activity types                         | Nominal                |
| **Developmental factors**     | Lexical diversity                      | Continuous numeric     |
|                               | Average sentence length                | Continuous numeric     |

*The table lists the factor categories, the individual variables measured within each category, and the type of variable (numeric / nominal, continuous / discrete).*

---

## Data


**Table 2 – Summary of the French‑language corpora used**

| Corpus      | No. of children | Age range | Total # of recorded sessions |
|-------------|-----------------|-----------|------------------------------|
| Champaud    | 1               | 1;9‑2;5   | 10                           |
| Geneva      | 2               | 1;3‑2;6   | 40                           |
| Hunkeler    | 2               | 1;6‑2;6   | 47                           |
| Kern‑French | 4               | 1;3‑2;2   | 129                          |
| Leveillé    | 1               | 2;1‑3;3   | 33                           |
| French‑Lyon | 5               | 1;0‑3;0   | 393                          |
| Palasis     | 22              | 0;7‑2;0   | 23                           |
| Paris       | 7               | 0;7‑6;3   | 230                          |
| Pauline     | 1               | 1;2‑2;6   | 33                           |
| Yamaguchi   | 1               | 1;11‑4;3  | 31                           |
| York        | 3               | 1;9‑4;3   | 107                          |
| **Total**   | 49              | 0;7‑6;3   | 1,076                        |

*Columns: Corpus name, number of children recorded, age interval, and total number of sessions recorded for all children combined.*

> **Privacy Note** – All the data used is classified as *open access* by CHILDES and is available under the Creative Commons CC BY-NC-SA 3.0 copyright license . (For more detail see [basic rules](https://talkbank.org/0share/rules.html) or [ground rules](https://talkbank.org/0share/index.html))

---

## Repository Structure

```
.
├── data #The data folder is placed outsid the project repo
│   ├── data_fan_valence.csv
│   ├── data_lexique382.tsv
│   ├── data_semantiqc_imagea.csv
│   └── French-Corpa
│       ├── Champaud010906x.cha
│       ├── Champaud010918.cha
│       └── … (other .cha files)
├── analyse_mots_abstraits #The git folder repo
│   ├── module
│   │   ├── __init__.py
│   │   ├── annotator.py
│   │   ├── childes_parser.py
│   │   ├── custom_panda_saver.py
│   │   └── tokenisation.py
│   ├── old_script
│   │   ├── analyse_all.py
│   │   ├── analyse_charactere.py
│   │   ... (other old .py script)
│   ├── .gitignore
│   ├── LICENSE
│   ├── main.py
│   ├── README.md
│   └── TODO.md
└── results #Where the results will be saved
    ├── log.txt
    ├── french_corpa_parsed1.tsv
    ├── french_corpa_token1.tsv
    ├── french_corpa_annotated1.tsv
    ├── child_dico1.tsv
    └── over_dico1.tsv
```

---

## Setup (Canvas : to be updated)

The project is written in **Python 3.10+**.  
We recommend using a virtual environment (venv or conda).

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate.bat    # Windows

# Install dependencies
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`)

```
spacy==3.7.0          # Tokenisation & POS‑tagging
pandas==2.2.2
tqdm==4.66.2
```

> *If you prefer Stanford CoreNLP, install the Java runtime and update `tokenisation.py` accordingly.*

---

## Usage  (Canvas : to be updated)

### 1. Tokenisation & POS‑Tagging

```bash
python src/tokenisation.py \
    --input data/raw/child_speech.tsv \
    --output data/processed/tokenised.tsv
```

This script reads the TSV, tokenises each sentence, tags the tokens, and writes a new TSV where each row contains:

| id | speaker | token | pos | original_sentence |

### 2. Abstract‑Noun Annotation

```bash
python src/annotate.py \
    --input data/processed/tokenised.tsv \
    --noun-list data/abstract_nouns_list.txt \
    --output data/processed/annotated.tsv
```

The output TSV has the same columns as the tokenised file plus a new column `is_abstract_noun` (`True/False`).

---

## Output  (Canvas : to be updated)

```
id    speaker    token   pos   is_abstract_noun   original_sentence
001   child1     freedom NN    True                "We should have freedom."
002   child1     and     CC    False               "We should have freedom."
003   child1     peace   NN    False               "We should have freedom."
...
```

The annotated file can be directly imported into statistical software (R, SPSS, Python) for frequency counts, chi‑square tests, or regression modelling.

---

## Results & Analysis  (Canvas : to be updated)

The annotated data feed into the following analyses (see `notebooks/analysis.ipynb`):

| Analysis | Description |
|----------|-------------|
| Frequency of abstract noun usage by age group | How early children start using abstract concepts. |
| Contextual co‑occurrence | What words surround abstract nouns (semantic clustering). |
| Parent vs. peer influence | Comparing usage in child‑parent vs. child‑child contexts. |

A brief summary of the findings:

- **Finding 1:** Blabla  
- **Finding 2:** Blabla

---

## Future Work  (Canvas : to be updated)

- **Automatic concept extraction** using word‑embedding similarity (e.g., GloVe, BERT).  
- **Longitudinal tracking** of the same children over multiple years.  
- **Cross‑linguistic comparison** (English vs. other languages).  
- **Modeling developmental trajectories** via growth‑curve analysis.

---
 

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## Contact  (Canvas to be updated)

| Name | Email | Role |
|------|-------|------|
| Dr. Jane Doe | jane.doe@university.edu | Project Lead |
| Alex Smith | alex.smith@university.edu | Data Scientist |

Feel free to open an issue or email for questions, suggestions, or collaboration ideas.

---

*Happy analyzing!*