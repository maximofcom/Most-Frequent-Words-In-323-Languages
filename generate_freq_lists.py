import sys
import re
import random
from collections import Counter
import mwparserfromhell
from datasets import load_dataset
import time

# Set seed
random.seed(42)

import sys
import re
import random
from collections import Counter
import mwparserfromhell
from datasets import load_dataset, get_dataset_config_names
import time

# Set seed
random.seed(42)

def get_latest_configs():
    print("Fetching dataset configurations...")
    try:
        all_configs = get_dataset_config_names("wikimedia/wikipedia")
    except Exception as e:
        print(f"Failed to fetch configs: {e}")
        return []

    lang_map = {}
    for c in all_configs:
        parts = c.split('.')
        if len(parts) != 2:
            continue
        date, lang = parts
        # Simple date comparison (string compare works for YYYYMMDD)
        if lang not in lang_map or date > lang_map[lang]:
            lang_map[lang] = date
            
    # Return list of (lang, config_name) sorted by lang
    configs = [(l, f"{d}.{l}") for l, d in lang_map.items()]
    configs.sort()
    print(f"Found {len(configs)} languages.")
    return configs

def clean_text(raw_text):
    try:
        # mwparserfromhell can be slow or fail on huge texts, simple protection
        parsed = mwparserfromhell.parse(raw_text)
        return parsed.strip_code()
    except Exception:
        return raw_text

def detect_regex(text_sample):
    # Define candidate regexes for different scripts
    # Using specific ranges to be precise
    definitions = [
        ('latin', r'[a-z\u00C0-\u00FF\u0100-\u017F]+'),
        ('cyrillic', r'[\u0400-\u04FF]+'),
        ('arabic', r'[\u0600-\u06FF]+'),
        ('devanagari', r'[\u0900-\u097F]+'),
        ('bengali', r'[\u0980-\u09FF]+'),
        ('gurmukhi', r'[\u0A00-\u0A7F]+'),
        ('gujarati', r'[\u0A80-\u0AFF]+'),
        ('oriya', r'[\u0B00-\u0B7F]+'),
        ('tamil', r'[\u0B80-\u0BFF]+'),
        ('telugu', r'[\u0C00-\u0C7F]+'),
        ('kannada', r'[\u0C80-\u0CFF]+'),
        ('malayalam', r'[\u0D00-\u0D7F]+'),
        ('sinhala', r'[\u0D80-\u0DFF]+'),
        ('thai', r'[\u0E00-\u0E7F]+'),
        ('lao', r'[\u0E80-\u0EFF]+'),
        ('tibetan', r'[\u0F00-\u0FFF]+'),
        ('myanmar', r'[\u1000-\u109F]+'),
        ('georgian', r'[\u10A0-\u10FF]+'),
        ('hangul', r'[\uAC00-\uD7AF]+'), # Korean
        ('cjk', r'[\u4E00-\u9FFF]'), # Chinese (single char)
        ('hiragana_katakana', r'[\u3040-\u309F\u30A0-\u30FF]+'), # Japanese Kana
        ('hebrew', r'[\u0590-\u05FF]+'),
        ('greek', r'[\u0370-\u03FF]+'),
        ('armenian', r'[\u0530-\u058F]+'),
    ]
    
    # Normalize sample
    sample = text_sample.lower()
    
    scores = []
    for name, pattern in definitions:
        # Find all matches
        matches = re.findall(pattern, sample)
        # Score is total length of matches
        score = sum(len(m) for m in matches)
        scores.append((score, pattern, name))
        
    # Sort by score desc
    scores.sort(key=lambda x: x[0], reverse=True)
    
    best_score, best_pattern, best_name = scores[0]
    
    if best_score == 0:
        # Fallback to latin if nothing matches (unlikely for Wikipedia)
        return r'[a-z]+'
        
    # Special handling: 
    # If it's CJK, we used single char regex, which is correct.
    # If it's Japanese, it might be mixed. 
    # If 'hiragana_katakana' wins, we might want to include CJK chars too because Kanji is used in JA.
    # But the prompt says "native alphabet". Kanji IS native to JA writing.
    # If 'cjk' wins (Chinese), it's fine.
    
    return best_pattern

def get_tokens(text, regex_pattern):
    text = text.lower()
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)
    # Find all matches
    tokens = re.findall(regex_pattern, text)
    return tokens

def process_language(lang_code, dataset_name, target_count):
    print(f"Processing {lang_code} ({dataset_name})...")
    
    # Load dataset in streaming mode
    try:
        ds = load_dataset("wikimedia/wikipedia", dataset_name, split="train", streaming=True)
    except Exception as e:
        print(f"Error loading {dataset_name}: {e}")
        return

    # Reservoir sampling
    reservoir = []
    MAX_SCAN = 200000 
    
    try:
        iterator = iter(ds)
        for i in range(MAX_SCAN):
            try:
                article = next(iterator)
            except StopIteration:
                break
                
            text = article.get('text', '')
            if not text:
                continue
                
            if len(reservoir) < target_count:
                reservoir.append(text)
            else:
                j = random.randint(0, i)
                if j < target_count:
                    reservoir[j] = text
            
            if i % 10000 == 0 and i > 0:
                print(f"  Scanned {i} articles...", end='\r')
                
    except Exception as e:
        print(f"Stream interrupted: {e}")

    print(f"\nCollected {len(reservoir)} articles for {lang_code}")
    
    if not reservoir:
        print("No articles found.")
        return

    # Determine regex from a large sample (first 50 articles)
    print("  Detecting script...")
    sample_text = " ".join(reservoir[:50])
    regex = detect_regex(sample_text)
    print(f"  Using regex: {regex}")
    
    # Process text
    all_tokens = []
    print("  Tokenizing...")
    for text in reservoir:
        cleaned = clean_text(text)
        tokens = get_tokens(cleaned, regex)
        all_tokens.extend(tokens)
        
    # Frequency analysis
    counter = Counter(all_tokens)
    most_common = counter.most_common(1000000)
    
    # Save
    filename = f"freq_{lang_code}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for word, freq in most_common:
            f.write(f"{word} {freq}\n")
    print(f"Saved {filename}")

def main():
    configs = get_latest_configs()
    
    if not configs:
        print("No configurations found. Exiting.")
        return
        
    for lang, config_name in configs:
        process_language(lang, config_name, 100000)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
