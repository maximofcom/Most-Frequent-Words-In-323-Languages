---

# 📚 Multilingual Wikipedia Word Frequency Lists

This repository contains automatically generated **word frequency lists for all languages available in the Wikimedia Wikipedia dataset**.  
The lists are created using a unified, reproducible pipeline that performs:

- streaming data extraction  
- reservoir sampling  
- wiki markup cleaning  
- script detection  
- tokenization  
- frequency analysis  

The goal is to provide clean, comparable lexical resources for multilingual NLP, linguistics, and language modeling.

---

## 🚀 Features

- Supports **all languages** in the `wikimedia/wikipedia` dataset  
- **Streaming mode** — no full dumps downloaded  
- **Reservoir sampling** — unbiased random selection  
- **Seeded randomness** (`seed = 42`) — fully reproducible  
- Automatic **script detection** (Latin, Cyrillic, Devanagari, Hangul, CJK, Arabic, etc.)  
- Cleans wiki markup using `mwparserfromhell`  
- Generates up to **1,000,000 most frequent words** per language  
- Saves results in simple `.txt` files  

---

## 📦 Output Format

Each language produces a file:

```
freq_<language_code>.txt
```

Example:

```
freq_en.txt
freq_ru.txt
freq_uz.txt
freq_hi.txt
freq_ko.txt
```

Each file contains tab‑separated pairs:

```
word frequency
```

Example:

```
the 123456
and 98765
to 87654
```

---

## 🧠 How It Works

### 1. Fetch Latest Wikipedia Configurations
The script automatically identifies the **latest dump date** for each language:

```python
get_dataset_config_names("wikimedia/wikipedia")
```

It selects the newest `<date>.<lang>` configuration for every language.

---

### 2. Streaming + Reservoir Sampling

For each language:

- The dataset is streamed (no full download)
- Up to **200,000 articles** are scanned
- Exactly **100 articles** are selected using reservoir sampling
- Randomness is controlled with:

```python
random.seed(42)
```

This ensures reproducibility.

---

### 3. Wiki Markup Cleaning

Each article’s `text` field is cleaned using:

```python
mwparserfromhell.parse(raw).strip_code()
```

This removes:

- templates  
- tables  
- categories  
- HTML tags  
- wiki links  
- formatting  

---

### 4. Script Detection

A sample of the collected articles is analyzed to determine the dominant writing system.  
The script detector supports:

- Latin  
- Cyrillic  
- Arabic  
- Devanagari  
- Hangul  
- CJK  
- Hebrew  
- Greek  
- Armenian  
- and many more  

The detector selects the regex with the highest match score.

---

### 5. Tokenization

Tokens are extracted using the detected script regex.  
The pipeline:

- lowercases all text  
- removes digits  
- removes punctuation  
- removes URLs  
- keeps only alphabetic tokens in the native script  
- does **not** perform lemmatization  

---

### 6. Frequency Analysis

All tokens are counted using `collections.Counter`.

The top **1,000,000** words (or fewer if the language has fewer unique tokens) are saved.

---

## 📁 File Structure

```
.
├── freq_en.txt
├── freq_ru.txt
├── freq_uz.txt
├── freq_hi.txt
├── freq_ko.txt
├── freq_<lang>.txt
└── script.py
```

---

## 🛠 Dependencies

- Python 3.9+
- datasets
- mwparserfromhell

Install:

```bash
pip install datasets mwparserfromhell
```

---

## ▶️ Running the Script

```bash
python script.py
```

The script will:

1. detect all available Wikipedia languages  
2. sample 100 articles per language  
3. generate frequency lists  
4. save them to `freq_<lang>.txt`  

