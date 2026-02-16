#!/usr/bin/env python3
"""
Generate 500 minimal pairs CSV dataset for Old Norse grammatical evaluation.
125 pairs per phenomenon: QUIRKY_CASE, ADJECTIVE, UMLAUT, MIDDLE_VOICE
"""

import csv
import random
from typing import List, Optional
from dataclasses import dataclass

try:
    import norsecorpus.reader as ncr
    HAS_CORPUS = True
except ImportError:
    HAS_CORPUS = False

from generate_rules import (
    DATIVE_VERBS, DATIVE_TO_NOMINATIVE, DATIVE_PRONOUNS,
    U_UMLAUT_CORRECT_TO_INCORRECT,
    MIDDLE_VOICE_TO_ACTIVE,
    ADJECTIVE_STEMS,
)


@dataclass
class MinimalPair:
    id: str
    phenomenon: str
    grammatical: str
    ungrammatical: str
    target: str
    error_type: str


# =============================================================================
# SENTENCE TEMPLATES FOR SYNTHETIC GENERATION
# =============================================================================

# Names from textbook
NAMES = ['Óláfr', 'Sigurðr', 'Eiríkr', 'Ragnarr', 'Haukr', 'Svartr', 'Kormákr', 
         'Þórr', 'Óðinn', 'Baldr', 'Njáll', 'Gunnarr', 'Skarpheðinn', 'Flosi']

# Nouns (nominative)
NOUNS_NOM = ['konungr', 'jarl', 'maðr', 'víkingr', 'draugr', 'dvergr', 'úlfr', 
             'ormr', 'hestr', 'haukr', 'brandr', 'baugr', 'hjálmr']

# Nouns (accusative)
NOUNS_ACC = ['konung', 'jarl', 'mann', 'víking', 'draug', 'dverg', 'úlf',
             'orm', 'hest', 'hauk', 'brand', 'baug', 'hjálm']

# Dative pronouns with their nominative forms
DATIVE_NOM_PAIRS = [
    ('mér', 'ek'), ('þér', 'þú'), ('hánum', 'hann'), ('honum', 'hann'),
    ('henni', 'hon'), ('því', 'þat'), ('oss', 'vér'), ('yðr', 'þér'),
    ('þeim', 'þeir'), ('okkr', 'vit'),
]

# Verbs that take dative
DATIVE_VERB_FORMS = ['gefr', 'segir', 'sýnir', 'fœrir', 'býðr', 'hjálpar', 'trúir']

# U-umlaut pairs (correct -> incorrect)
UMLAUT_PAIRS = [
    ('mönnum', 'mannum'), ('tökum', 'takum'), ('köllum', 'kallum'),
    ('höfum', 'hafum'), ('förum', 'farum'), ('stöndum', 'standum'),
    ('göngum', 'gangum'), ('glöðum', 'glaðum'), ('öllum', 'allum'),
    ('öðrum', 'aðrum'), ('jörlum', 'jarlum'), ('vöngum', 'vangum'),
    ('löngum', 'langum'), ('rögum', 'ragum'), ('mörgum', 'margum'),
]

# Middle voice pairs (correct -> incorrect)  
MIDDLE_PAIRS = [
    ('kallask', 'kalla'), ('finnask', 'finna'), ('hittask', 'hitta'),
    ('takask', 'taka'), ('gerask', 'gera'), ('setjask', 'setja'),
    ('leggjask', 'leggja'), ('berjask', 'berja'), ('snúask', 'snúa'),
    ('kallast', 'kallar'), ('finnst', 'finnr'), ('hittust', 'hittu'),
    ('fundusk', 'fundu'), ('settust', 'settu'), ('tókusk', 'tóku'),
    ('gerðusk', 'gerðu'), ('börðusk', 'börðu'),
]

# Adjective stems with strong forms
ADJ_STRONG_FORMS = [
    ('góðr', 'góði', 'góð'), ('illr', 'illi', 'ill'), ('stórr', 'stóri', 'stór'),
    ('langr', 'langi', 'lang'), ('reiðr', 'reiði', 'reið'), ('glaðr', 'glaði', 'glað'),
    ('ríkr', 'ríki', 'rík'), ('ungr', 'ungi', 'ung'), ('gamall', 'gamli', 'gamal'),
    ('spakr', 'spaki', 'spak'), ('sterkr', 'sterki', 'sterk'), ('víss', 'vísi', 'vís'),
    ('fagr', 'fagri', 'fag'), ('harðr', 'harði', 'harð'), ('frœkn', 'frœkni', 'frœkn'),
]

# Strong accusative -> weak
ADJ_ACC_FORMS = [
    ('góðan', 'góða'), ('illan', 'illa'), ('stóran', 'stóra'),
    ('langan', 'langa'), ('reiðan', 'reiða'), ('glaðan', 'glaða'),
    ('ríkan', 'ríka'), ('ungan', 'unga'), ('gamlan', 'gamla'),
    ('spakan', 'spaka'), ('sterkan', 'sterka'), ('vísan', 'vísa'),
    ('fagran', 'fagra'), ('harðan', 'harða'),
]


# =============================================================================
# CORPUS LOADING
# =============================================================================

def load_corpus_sentences() -> List[str]:
    """Load sentences from corpus."""
    if not HAS_CORPUS:
        return []
    
    sentences = []
    for filename, filepath in ncr.get_available_texts().items():
        try:
            for chapter in ncr.read_tei_words(filepath):
                for para in chapter:
                    for sent in para:
                        if sent:
                            text = ' '.join(sent)
                            words = text.split()
                            if 4 <= len(words) <= 25 and not any(c in text for c in '[](){}<>'):
                                sentences.append(text)
        except:
            continue
    return sentences


# =============================================================================
# QUIRKY CASE GENERATION (125 pairs)
# =============================================================================

def generate_quirky_case_pairs(corpus_sents: List[str], target: int = 125) -> List[MinimalPair]:
    """Generate QUIRKY_CASE minimal pairs."""
    pairs = []
    pair_num = 1
    used_sents = set()
    
    # First, extract from corpus
    for sent in corpus_sents:
        if len(pairs) >= target:
            break
        words = sent.split()
        for i, word in enumerate(words):
            w = word.lower().rstrip('.,;:!?')
            if w in DATIVE_TO_NOMINATIVE:
                context = [x.lower().rstrip('.,;:!?') for x in words[max(0,i-2):i+3]]
                if any(v in DATIVE_VERBS for v in context):
                    if sent not in used_sents:
                        punct = word[len(w):] if len(word) > len(w) else ''
                        wrong = DATIVE_TO_NOMINATIVE[w]
                        if word[0].isupper():
                            wrong = wrong.capitalize()
                        new_words = words.copy()
                        new_words[i] = wrong + punct
                        pairs.append(MinimalPair(
                            f"ON_QUIRKY_CASE_{pair_num:03d}", "QUIRKY_CASE",
                            sent, ' '.join(new_words), word.rstrip('.,;:!?'), "dative_to_nominative"
                        ))
                        pair_num += 1
                        used_sents.add(sent)
                        break
    
    # Generate synthetic sentences to reach target
    templates = [
        "{name} {verb} {dat} {noun}.",
        "{verb} {dat} {noun} {name}.",
        "Þá {verb} {dat} {noun}.",
        "Nú {verb} {name} {dat} {noun}.",
        "{name} {verb} {dat} góðan {noun}.",
        "Hér {verb} {dat} stóran {noun}.",
        "{name} konungr {verb} {dat} {noun}.",
        "Jarl {verb} {dat} {noun} ok mælir.",
        "{verb} {dat} {noun} , segir {name}.",
        "Þeir {verb} {dat} marga {noun}a.",
    ]
    
    while len(pairs) < target:
        dat, nom = random.choice(DATIVE_NOM_PAIRS)
        verb = random.choice(DATIVE_VERB_FORMS)
        name = random.choice(NAMES)
        noun = random.choice(NOUNS_ACC)
        template = random.choice(templates)
        
        grammatical = template.format(name=name, verb=verb, dat=dat, noun=noun)
        ungrammatical = template.format(name=name, verb=verb, dat=nom, noun=noun)
        
        if grammatical not in used_sents:
            pairs.append(MinimalPair(
                f"ON_QUIRKY_CASE_{pair_num:03d}", "QUIRKY_CASE",
                grammatical, ungrammatical, dat, "dative_to_nominative"
            ))
            pair_num += 1
            used_sents.add(grammatical)
    
    return pairs[:target]


# =============================================================================
# UMLAUT GENERATION (125 pairs)
# =============================================================================

def generate_umlaut_pairs(corpus_sents: List[str], target: int = 125) -> List[MinimalPair]:
    """Generate UMLAUT minimal pairs."""
    pairs = []
    pair_num = 1
    used_sents = set()
    
    # Extract from corpus
    for sent in corpus_sents:
        if len(pairs) >= target:
            break
        words = sent.split()
        for i, word in enumerate(words):
            w = word.lower().rstrip('.,;:!?')
            if w in U_UMLAUT_CORRECT_TO_INCORRECT:
                if sent not in used_sents:
                    punct = word[len(w):] if len(word) > len(w) else ''
                    wrong = U_UMLAUT_CORRECT_TO_INCORRECT[w]
                    if word[0].isupper():
                        wrong = wrong.capitalize()
                    new_words = words.copy()
                    new_words[i] = wrong + punct
                    pairs.append(MinimalPair(
                        f"ON_UMLAUT_{pair_num:03d}", "UMLAUT",
                        sent, ' '.join(new_words), word.rstrip('.,;:!?'), "umlaut_removed"
                    ))
                    pair_num += 1
                    used_sents.add(sent)
                    break
    
    # Generate synthetic
    templates = [
        "Vér {umlaut} nú til skógar.",
        "Þeir gefa {umlaut} mat.",
        "Vér {umlaut} hér ok bíðum.",
        "{name} gefr {umlaut} baug.",
        "Þeir fara til {umlaut}.",
        "Vér {umlaut} ok sjám {name}.",
        "Konungr gefr {umlaut} gull.",
        "Þeir mæla við {umlaut}.",
        "Vér {umlaut} heim ok hvílumsk.",
        "{name} segir {umlaut} frá því.",
    ]
    
    while len(pairs) < target:
        correct, incorrect = random.choice(UMLAUT_PAIRS)
        name = random.choice(NAMES)
        template = random.choice(templates)
        
        grammatical = template.format(umlaut=correct, name=name)
        ungrammatical = template.format(umlaut=incorrect, name=name)
        
        if grammatical not in used_sents:
            pairs.append(MinimalPair(
                f"ON_UMLAUT_{pair_num:03d}", "UMLAUT",
                grammatical, ungrammatical, correct, "umlaut_removed"
            ))
            pair_num += 1
            used_sents.add(grammatical)
    
    return pairs[:target]


# =============================================================================
# MIDDLE VOICE GENERATION (125 pairs)
# =============================================================================

def generate_middle_voice_pairs(corpus_sents: List[str], target: int = 125) -> List[MinimalPair]:
    """Generate MIDDLE_VOICE minimal pairs."""
    pairs = []
    pair_num = 1
    used_sents = set()
    
    # Extract from corpus
    for sent in corpus_sents:
        if len(pairs) >= target:
            break
        words = sent.split()
        for i, word in enumerate(words):
            w = word.lower().rstrip('.,;:!?')
            if w in MIDDLE_VOICE_TO_ACTIVE:
                if sent not in used_sents:
                    punct = word[len(w):] if len(word) > len(w) else ''
                    wrong = MIDDLE_VOICE_TO_ACTIVE[w]
                    if word[0].isupper():
                        wrong = wrong.capitalize()
                    new_words = words.copy()
                    new_words[i] = wrong + punct
                    pairs.append(MinimalPair(
                        f"ON_MIDDLE_VOICE_{pair_num:03d}", "MIDDLE_VOICE",
                        sent, ' '.join(new_words), word.rstrip('.,;:!?'), "middle_voice_removed"
                    ))
                    pair_num += 1
                    used_sents.add(sent)
                    break
    
    # Generate synthetic
    templates = [
        "Þeir {mid} í morgin.",
        "{name} ok {name2} {mid} þar.",
        "Menn {mid} við ána.",
        "Þeir {mid} ok mæla saman.",
        "Víkingar {mid} á hólminum.",
        "{name} {mid} konungr.",
        "Þeir {mid} í bardaga.",
        "Menn {mid} í skóginum.",
        "{name} ok jarl {mid} þar.",
        "Þeir {mid} ok fara heim.",
        "Konungar {mid} í Noregi.",
        "{name} {mid} við {name2}.",
        "Þeir {mid} um daginn.",
        "Menn {mid} ok berjask.",
        "{name} {mid} ríkr maðr.",
    ]
    
    while len(pairs) < target:
        correct, incorrect = random.choice(MIDDLE_PAIRS)
        name = random.choice(NAMES)
        name2 = random.choice([n for n in NAMES if n != name])
        template = random.choice(templates)
        
        grammatical = template.format(mid=correct, name=name, name2=name2)
        ungrammatical = template.format(mid=incorrect, name=name, name2=name2)
        
        if grammatical not in used_sents:
            pairs.append(MinimalPair(
                f"ON_MIDDLE_VOICE_{pair_num:03d}", "MIDDLE_VOICE",
                grammatical, ungrammatical, correct, "middle_voice_removed"
            ))
            pair_num += 1
            used_sents.add(grammatical)
    
    return pairs[:target]


# =============================================================================
# ADJECTIVE GENERATION (125 pairs)
# =============================================================================

def generate_adjective_pairs(corpus_sents: List[str], target: int = 125) -> List[MinimalPair]:
    """Generate ADJECTIVE minimal pairs."""
    pairs = []
    pair_num = 1
    used_sents = set()
    
    # Extract from corpus
    for sent in corpus_sents:
        if len(pairs) >= target:
            break
        words = sent.split()
        for i, word in enumerate(words):
            w = word.lower().rstrip('.,;:!?')
            # Check strong nominative forms
            for strong, weak, stem in ADJ_STRONG_FORMS:
                if w == strong:
                    if sent not in used_sents:
                        punct = word[len(w):] if len(word) > len(w) else ''
                        wrong = weak
                        if word[0].isupper():
                            wrong = wrong.capitalize()
                        new_words = words.copy()
                        new_words[i] = wrong + punct
                        pairs.append(MinimalPair(
                            f"ON_ADJECTIVE_{pair_num:03d}", "ADJECTIVE",
                            sent, ' '.join(new_words), word.rstrip('.,;:!?'), "strong_to_weak"
                        ))
                        pair_num += 1
                        used_sents.add(sent)
                        break
            # Check strong accusative forms
            for strong_acc, weak_acc in ADJ_ACC_FORMS:
                if w == strong_acc:
                    if sent not in used_sents:
                        punct = word[len(w):] if len(word) > len(w) else ''
                        wrong = weak_acc
                        if word[0].isupper():
                            wrong = wrong.capitalize()
                        new_words = words.copy()
                        new_words[i] = wrong + punct
                        pairs.append(MinimalPair(
                            f"ON_ADJECTIVE_{pair_num:03d}", "ADJECTIVE",
                            sent, ' '.join(new_words), word.rstrip('.,;:!?'), "strong_to_weak"
                        ))
                        pair_num += 1
                        used_sents.add(sent)
                        break
    
    # Generate synthetic - nominative
    nom_templates = [
        "{name} er {adj} maðr.",
        "Hann er {adj} konungr.",
        "{adj} maðr heitir {name}.",
        "Þar býr {adj} jarl.",
        "{name} var {adj} ok ríkr.",
        "Hann var {adj} mjök.",
        "{adj} víkingr kemr þar.",
        "Sá er {adj} maðr.",
        "{name} er {adj} ok sterkr.",
        "Þar er {adj} skógr.",
    ]
    
    # Generate synthetic - accusative
    acc_templates = [
        "{name} sér {adj} mann.",
        "Hann á {adj} hest.",
        "Þeir finna {adj} konung.",
        "{name} vegr {adj} úlf.",
        "Hann tekr {adj} brand.",
        "Þeir sjá {adj} orm.",
        "{name} hefir {adj} hjálm.",
        "Konungr á {adj} baug.",
        "Þeir fœra {adj} mat.",
        "Hann kaupir {adj} hest.",
    ]
    
    while len(pairs) < target:
        if random.random() < 0.5:
            # Nominative
            strong, weak, stem = random.choice(ADJ_STRONG_FORMS)
            template = random.choice(nom_templates)
            name = random.choice(NAMES)
            grammatical = template.format(adj=strong, name=name)
            ungrammatical = template.format(adj=weak, name=name)
            target_word = strong
        else:
            # Accusative
            strong_acc, weak_acc = random.choice(ADJ_ACC_FORMS)
            template = random.choice(acc_templates)
            name = random.choice(NAMES)
            grammatical = template.format(adj=strong_acc, name=name)
            ungrammatical = template.format(adj=weak_acc, name=name)
            target_word = strong_acc
        
        if grammatical not in used_sents:
            pairs.append(MinimalPair(
                f"ON_ADJECTIVE_{pair_num:03d}", "ADJECTIVE",
                grammatical, ungrammatical, target_word, "strong_to_weak"
            ))
            pair_num += 1
            used_sents.add(grammatical)
    
    return pairs[:target]


# =============================================================================
# MAIN GENERATION
# =============================================================================

def generate_dataset(output_path: str = "minimal_pairs.csv"):
    """Generate 500 minimal pairs (125 per phenomenon)."""
    print("=" * 60)
    print("OLD NORSE MINIMAL PAIRS DATASET GENERATOR")
    print("=" * 60)
    
    print("\nLoading corpus...")
    corpus = load_corpus_sentences()
    print(f"Loaded {len(corpus)} sentences from corpus")
    
    print("\nGenerating 125 pairs per phenomenon...")
    
    # Generate each type
    print("  QUIRKY_CASE...")
    quirky = generate_quirky_case_pairs(corpus, 125)
    print(f"    Generated {len(quirky)} pairs")
    
    print("  UMLAUT...")
    umlaut = generate_umlaut_pairs(corpus, 125)
    print(f"    Generated {len(umlaut)} pairs")
    
    print("  MIDDLE_VOICE...")
    middle = generate_middle_voice_pairs(corpus, 125)
    print(f"    Generated {len(middle)} pairs")
    
    print("  ADJECTIVE...")
    adjective = generate_adjective_pairs(corpus, 125)
    print(f"    Generated {len(adjective)} pairs")
    
    # Combine all
    all_pairs = quirky + umlaut + middle + adjective
    
    # Write CSV with UTF-8 BOM for Excel compatibility
    print(f"\nWriting {len(all_pairs)} pairs to {output_path}...")
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'phenomenon', 'grammatical', 'ungrammatical', 'target', 'error_type'])
        for p in all_pairs:
            writer.writerow([p.id, p.phenomenon, p.grammatical, p.ungrammatical, p.target, p.error_type])
    
    # Summary
    print("\n" + "=" * 60)
    print("DATASET CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"Output file: {output_path}")
    print(f"Total pairs: {len(all_pairs)}")
    print("\nDistribution:")
    print(f"  QUIRKY_CASE:  {len(quirky)}")
    print(f"  UMLAUT:       {len(umlaut)}")
    print(f"  MIDDLE_VOICE: {len(middle)}")
    print(f"  ADJECTIVE:    {len(adjective)}")
    
    # Show samples
    print("\n" + "-" * 60)
    print("SAMPLE PAIRS (one per phenomenon):")
    print("-" * 60)
    
    for pairs_list, name in [(quirky, "QUIRKY_CASE"), (umlaut, "UMLAUT"), 
                              (middle, "MIDDLE_VOICE"), (adjective, "ADJECTIVE")]:
        if pairs_list:
            p = pairs_list[0]
            print(f"\n{name}:")
            print(f"  Grammatical:   {p.grammatical}")
            print(f"  Ungrammatical: {p.ungrammatical}")
            print(f"  Target: {p.target} | Error: {p.error_type}")


if __name__ == "__main__":
    generate_dataset()
