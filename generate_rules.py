#!/usr/bin/env python3
"""
Comprehensive Rule-based Grammar System for Old Norse
Based on "Old Norse for Beginners" by Haukur Þorgeirsson and Óskar Guðlaugsson (Lessons 1-9)

NO LLM USAGE - Pure programmatic rule-based generation.

Grammar Rules from the textbook:
1. CASE SYSTEM: Nominative, Accusative, Dative, Genitive (Lessons 1, 4, 5, 7)
2. NOUN DECLENSION: Strong masculine a-stems and i-stems (Lessons 1, 2, 6, 8, 9)
3. ADJECTIVE DECLENSION: Strong (indefinite) vs Weak (definite) (Lesson 3)
4. PRONOUN DECLENSION: Personal, reflexive, demonstrative (Lessons 1, 2, 7, 8)
5. VERB CONJUGATION: Regular, irregular, present-preterite (Lessons 2, 3, 8)
6. U-UMLAUT: a→ö before -um endings (Lessons 2, 4, 6)
7. I-UMLAUT: Various vowel fronting patterns (Lesson 6)
8. ARTICLE SYSTEM: Suffixed definite article (Lessons 1, 3, 6)
9. WORD ORDER: V2 (Verb-Second) rule (Lessons 2, 6)
10. QUIRKY CASE: Verbs taking dative/genitive objects (Lessons 4, 5, 9)
11. MIDDLE VOICE: -sk/-st suffix for reflexive/reciprocal (Lesson 7)
12. PREPOSITIONS: Case governance (acc vs dat) (Lesson 5)
"""

import os
import csv
import random
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass


try:
    import norsecorpus.reader as ncr
    HAS_CORPUS = True
except ImportError:
    HAS_CORPUS = False


@dataclass
class MinimalPair:
    """A minimal pair with grammatical and ungrammatical variants."""
    id: str
    phenomenon: str
    grammatical: str
    ungrammatical: str
    target: str
    error_type: str


# =============================================================================
# LESSON 1: PRONOUNS - Nominative and Accusative Cases
# "In Norse, nouns and pronouns are declined in cases"
# =============================================================================

# Nominative case: Subject and complement (Lesson 1)
# "ek þú hann hon þat" - singular
NOMINATIVE_PRONOUNS = {
    # Singular (Lesson 1)
    'ek', 'þú', 'hann', 'hon', 'þat',
    # Dual (Lesson 2)
    'vit', 'þit',
    # Plural (Lesson 2)
    'vér', 'þér', 'þeir', 'þær', 'þau'
}

# Accusative case: Object and prepositional (Lesson 1)
# "mik þik hann hana þat" - singular
ACCUSATIVE_PRONOUNS = {
    # Singular (Lesson 1)
    'mik', 'þik', 'hann', 'hana', 'þat',
    # Dual (Lesson 2)
    'okkr', 'ykkr',
    # Plural (Lesson 2)
    'oss', 'yðr', 'þá', 'þær', 'þau'
}

# Dative case: Indirect object (Lesson 4)
# "mér þér hánum henni því" - singular
DATIVE_PRONOUNS = {
    # Singular
    'mér', 'þér', 'hánum', 'honum', 'henni', 'því',
    # Dual (same as accusative)
    'okkr', 'ykkr',
    # Plural
    'oss', 'yðr', 'þeim'
}

# Genitive case: Possession (Lesson 7)
GENITIVE_PRONOUNS = {
    # Singular
    'mín', 'þín', 'hans', 'hennar', 'þess',
    # Dual
    'okkar', 'ykkar',
    # Plural
    'vár', 'yðvar', 'þeira'
}

# Reflexive pronouns (Lesson 7)
# "When the object of a sentence is the same as its subject"
REFLEXIVE_PRONOUNS = {
    'sik': 'acc',   # himself/herself/itself/themselves (accusative)
    'sér': 'dat',   # himself/herself/itself/themselves (dative)
    'sín': 'gen',   # his/her/its/their own (genitive)
}


# =============================================================================
# PRONOUN CASE TRANSFORMATIONS
# =============================================================================

# Full pronoun declension table (Lessons 1, 2, 4, 7)
PRONOUN_DECLENSION = {
    # 1st person singular
    'ek':   {'nom': 'ek',   'acc': 'mik',  'dat': 'mér',   'gen': 'mín'},
    'mik':  {'nom': 'ek',   'acc': 'mik',  'dat': 'mér',   'gen': 'mín'},
    'mér':  {'nom': 'ek',   'acc': 'mik',  'dat': 'mér',   'gen': 'mín'},
    'mín':  {'nom': 'ek',   'acc': 'mik',  'dat': 'mér',   'gen': 'mín'},
    
    # 2nd person singular
    'þú':   {'nom': 'þú',   'acc': 'þik',  'dat': 'þér',   'gen': 'þín'},
    'þik':  {'nom': 'þú',   'acc': 'þik',  'dat': 'þér',   'gen': 'þín'},
    'þér':  {'nom': 'þú',   'acc': 'þik',  'dat': 'þér',   'gen': 'þín'},
    'þín':  {'nom': 'þú',   'acc': 'þik',  'dat': 'þér',   'gen': 'þín'},
    
    # 3rd person singular masculine
    'hann':   {'nom': 'hann', 'acc': 'hann', 'dat': 'hánum', 'gen': 'hans'},
    'hánum':  {'nom': 'hann', 'acc': 'hann', 'dat': 'hánum', 'gen': 'hans'},
    'honum':  {'nom': 'hann', 'acc': 'hann', 'dat': 'honum', 'gen': 'hans'},
    'hans':   {'nom': 'hann', 'acc': 'hann', 'dat': 'hánum', 'gen': 'hans'},
    
    # 3rd person singular feminine
    'hon':    {'nom': 'hon',  'acc': 'hana', 'dat': 'henni', 'gen': 'hennar'},
    'hana':   {'nom': 'hon',  'acc': 'hana', 'dat': 'henni', 'gen': 'hennar'},
    'henni':  {'nom': 'hon',  'acc': 'hana', 'dat': 'henni', 'gen': 'hennar'},
    'hennar': {'nom': 'hon',  'acc': 'hana', 'dat': 'henni', 'gen': 'hennar'},
    
    # 3rd person singular neuter
    'þat':  {'nom': 'þat',  'acc': 'þat',  'dat': 'því',   'gen': 'þess'},
    'því':  {'nom': 'þat',  'acc': 'þat',  'dat': 'því',   'gen': 'þess'},
    'þess': {'nom': 'þat',  'acc': 'þat',  'dat': 'því',   'gen': 'þess'},
    
    # 1st person dual
    'vit':   {'nom': 'vit',  'acc': 'okkr', 'dat': 'okkr',  'gen': 'okkar'},
    'okkr':  {'nom': 'vit',  'acc': 'okkr', 'dat': 'okkr',  'gen': 'okkar'},
    'okkar': {'nom': 'vit',  'acc': 'okkr', 'dat': 'okkr',  'gen': 'okkar'},
    
    # 2nd person dual
    'þit':   {'nom': 'þit',  'acc': 'ykkr', 'dat': 'ykkr',  'gen': 'ykkar'},
    'ykkr':  {'nom': 'þit',  'acc': 'ykkr', 'dat': 'ykkr',  'gen': 'ykkar'},
    'ykkar': {'nom': 'þit',  'acc': 'ykkr', 'dat': 'ykkr',  'gen': 'ykkar'},
    
    # 1st person plural
    'vér':   {'nom': 'vér',  'acc': 'oss',  'dat': 'oss',   'gen': 'vár'},
    'oss':   {'nom': 'vér',  'acc': 'oss',  'dat': 'oss',   'gen': 'vár'},
    'vár':   {'nom': 'vér',  'acc': 'oss',  'dat': 'oss',   'gen': 'vár'},
    
    # 2nd person plural
    'þér':   {'nom': 'þér',  'acc': 'yðr',  'dat': 'yðr',   'gen': 'yðvar'},
    'yðr':   {'nom': 'þér',  'acc': 'yðr',  'dat': 'yðr',   'gen': 'yðvar'},
    'yðvar': {'nom': 'þér',  'acc': 'yðr',  'dat': 'yðr',   'gen': 'yðvar'},
    
    # 3rd person plural masculine
    'þeir':  {'nom': 'þeir', 'acc': 'þá',   'dat': 'þeim',  'gen': 'þeira'},
    'þá':    {'nom': 'þeir', 'acc': 'þá',   'dat': 'þeim',  'gen': 'þeira'},
    'þeim':  {'nom': 'þeir', 'acc': 'þá',   'dat': 'þeim',  'gen': 'þeira'},
    'þeira': {'nom': 'þeir', 'acc': 'þá',   'dat': 'þeim',  'gen': 'þeira'},
    
    # 3rd person plural feminine
    'þær':   {'nom': 'þær',  'acc': 'þær',  'dat': 'þeim',  'gen': 'þeira'},
    
    # 3rd person plural neuter
    'þau':   {'nom': 'þau',  'acc': 'þau',  'dat': 'þeim',  'gen': 'þeira'},
}


# =============================================================================
# LESSON 1-2: STRONG MASCULINE NOUN DECLENSION
# "The pattern of the strong masculine word is that they have the ending -r 
#  in the nominative"
# =============================================================================

# Strong masculine nouns from vocabulary (Lessons 1-9)
# Format: stem -> (nom_sg, gen_sg, nom_pl) for i-stem vs a-stem distinction
STRONG_MASCULINE_NOUNS = {
    # A-stem nouns (regular): gen_sg -s, nom_pl -ar
    'álfr':     {'stem': 'álf',     'gen_sg': 'álfs',     'nom_pl': 'álfar',    'type': 'a-stem'},
    'baugr':    {'stem': 'baug',    'gen_sg': 'baugs',    'nom_pl': 'baugar',   'type': 'a-stem'},
    'brandr':   {'stem': 'brand',   'gen_sg': 'brands',   'nom_pl': 'brandar',  'type': 'a-stem'},
    'dvergr':   {'stem': 'dverg',   'gen_sg': 'dvergs',   'nom_pl': 'dvergar',  'type': 'a-stem'},
    'draugr':   {'stem': 'draug',   'gen_sg': 'draugs',   'nom_pl': 'draugar',  'type': 'a-stem'},
    'hestr':    {'stem': 'hest',    'gen_sg': 'hests',    'nom_pl': 'hestar',   'type': 'a-stem'},
    'haukr':    {'stem': 'hauk',    'gen_sg': 'hauks',    'nom_pl': 'haukar',   'type': 'a-stem'},
    'hjálmr':   {'stem': 'hjálm',   'gen_sg': 'hjálms',   'nom_pl': 'hjálmar',  'type': 'a-stem'},
    'konungr':  {'stem': 'konung',  'gen_sg': 'konungs',  'nom_pl': 'konungar', 'type': 'a-stem'},
    'knífr':    {'stem': 'kníf',    'gen_sg': 'knífs',    'nom_pl': 'knífar',   'type': 'a-stem'},
    'ormr':     {'stem': 'orm',     'gen_sg': 'orms',     'nom_pl': 'ormar',    'type': 'a-stem'},
    'úlfr':     {'stem': 'úlf',     'gen_sg': 'úlfs',     'nom_pl': 'úlfar',    'type': 'a-stem'},
    'bátr':     {'stem': 'bát',     'gen_sg': 'báts',     'nom_pl': 'bátar',    'type': 'a-stem'},
    'geirr':    {'stem': 'geir',    'gen_sg': 'geirs',    'nom_pl': 'geirar',   'type': 'a-stem'},
    'vargr':    {'stem': 'varg',    'gen_sg': 'vargs',    'nom_pl': 'vargar',   'type': 'a-stem'},
    'víkingr':  {'stem': 'víking',  'gen_sg': 'víkings',  'nom_pl': 'víkingar', 'type': 'a-stem'},
    'þjófr':    {'stem': 'þjóf',    'gen_sg': 'þjófs',    'nom_pl': 'þjófar',   'type': 'a-stem'},
    'fiskr':    {'stem': 'fisk',    'gen_sg': 'fisks',    'nom_pl': 'fiskar',   'type': 'a-stem'},
    'ostr':     {'stem': 'ost',     'gen_sg': 'osts',     'nom_pl': 'ostar',    'type': 'a-stem'},
    'eldr':     {'stem': 'eld',     'gen_sg': 'elds',     'nom_pl': 'eldar',    'type': 'a-stem'},
    'vindr':    {'stem': 'vind',    'gen_sg': 'vinds',    'nom_pl': 'vindar',   'type': 'a-stem'},
    'oddr':     {'stem': 'odd',     'gen_sg': 'odds',     'nom_pl': 'oddar',    'type': 'a-stem'},
    'sandr':    {'stem': 'sand',    'gen_sg': 'sands',    'nom_pl': 'sandar',   'type': 'a-stem'},
    'hringr':   {'stem': 'hring',   'gen_sg': 'hrings',   'nom_pl': 'hringar',  'type': 'a-stem'},
    'hundr':    {'stem': 'hund',    'gen_sg': 'hunds',    'nom_pl': 'hundar',   'type': 'a-stem'},
    'viðr':     {'stem': 'við',     'gen_sg': 'viðs',     'nom_pl': 'viðar',    'type': 'a-stem'},
    'dómr':     {'stem': 'dóm',     'gen_sg': 'dóms',     'nom_pl': 'dómar',    'type': 'a-stem'},
    'askr':     {'stem': 'ask',     'gen_sg': 'asks',     'nom_pl': 'askar',    'type': 'a-stem'},
    
    # I-stem nouns: gen_sg -ar, nom_pl -ir
    'staðr':    {'stem': 'stað',    'gen_sg': 'staðar',   'nom_pl': 'staðir',   'type': 'i-stem'},
    'máttr':    {'stem': 'mátt',    'gen_sg': 'máttar',   'nom_pl': 'mættir',   'type': 'i-stem'},
    
    # Mixed (gen_sg -ar, nom_pl -ar)
    'skógr':    {'stem': 'skóg',    'gen_sg': 'skógar',   'nom_pl': 'skógar',   'type': 'mixed'},
    'matr':     {'stem': 'mat',     'gen_sg': 'matar',    'nom_pl': 'matir',    'type': 'mixed'},
    
    # Nouns without -r in nominative (Lesson 2)
    'jarl':     {'stem': 'jarl',    'gen_sg': 'jarls',    'nom_pl': 'jarlar',   'type': 'no-r'},
    'hrafn':    {'stem': 'hrafn',   'gen_sg': 'hrafns',   'nom_pl': 'hrafnar',  'type': 'no-r'},
    
    # Bisyllabic stems (Lesson 8)
    'hamarr':   {'stem': 'hamar',   'gen_sg': 'hamars',   'nom_pl': 'hamrar',   'type': 'bisyllabic'},
    'himinn':   {'stem': 'himin',   'gen_sg': 'himins',   'nom_pl': 'himnar',   'type': 'bisyllabic'},
    'jötunn':   {'stem': 'jötun',   'gen_sg': 'jötuns',   'nom_pl': 'jötnar',   'type': 'bisyllabic'},
    
    # Assimilative nouns (Lesson 8): -r assimilates to s/l/n
    'íss':      {'stem': 'ís',      'gen_sg': 'íss',      'nom_pl': 'ísar',     'type': 'assimilative'},
    'hóll':     {'stem': 'hól',     'gen_sg': 'hóls',     'nom_pl': 'hólar',    'type': 'assimilative'},
    'steinn':   {'stem': 'stein',   'gen_sg': 'steins',   'nom_pl': 'steinar',  'type': 'assimilative'},
}


# Irregular noun: maðr (Lesson 2)
# "We will now introduce a masculine noun that in its declension does not 
#  follow the patterns already described"
MADR_DECLENSION = {
    'nom_sg': 'maðr',    'acc_sg': 'mann',    'dat_sg': 'manni',   'gen_sg': 'manns',
    'nom_pl': 'menn',    'acc_pl': 'menn',    'dat_pl': 'mönnum',  'gen_pl': 'manna',
    # With article
    'nom_sg_def': 'maðrinn',  'acc_sg_def': 'manninn',  'dat_sg_def': 'manninum',  'gen_sg_def': 'mannsins',
    'nom_pl_def': 'menninir', 'acc_pl_def': 'mennina',  'dat_pl_def': 'mönnunum',  'gen_pl_def': 'mannanna',
}

# =============================================================================
# LESSON 1, 3: DEFINITE ARTICLE
# "The Norse article is a suffix depending on case, gender and number"
# =============================================================================

# Masculine article endings (Lesson 3)
MASCULINE_ARTICLE = {
    'nom_sg': 'inn',   'acc_sg': 'inn',   'dat_sg': 'inum',  'gen_sg': 'ins',
    'nom_pl': 'inir',  'acc_pl': 'ina',   'dat_pl': 'inum',  'gen_pl': 'inna',
}

# Article attachment rules (Lesson 3):
# - If noun ends with vowel or 'r', drop the 'i' of article
# Examples: ormar + inir = ormarnir, orma + ina = ormana

def attach_article(noun_form: str, article: str) -> str:
    """Attach definite article to noun following textbook rules."""
    if noun_form.endswith('r') or noun_form[-1] in 'aeiouáéíóúöæœý':
        # Drop initial 'i' from article
        if article.startswith('i'):
            article = article[1:]
    return noun_form + article


# =============================================================================
# LESSON 3: ADJECTIVE DECLENSION - Strong (Indefinite) vs Weak (Definite)
# "In Old Norse adjectives have different forms depending on the number and 
#  case of the noun they describe"
# =============================================================================

# Strong adjective endings - masculine (used WITHOUT article)
# From textbook: "reiðr" (nom sg), "reiðan" (acc sg), "reiðir" (nom pl)
STRONG_ADJ_ENDINGS_MASC = {
    'nom_sg': 'r',     # reiðr, góðr, stórr
    'acc_sg': 'an',    # reiðan, góðan, stóran
    'dat_sg': 'um',    # reiðum, góðum, stórum
    'gen_sg': 's',     # reiðs, góðs, stórs
    'nom_pl': 'ir',    # reiðir, góðir, stórir
    'acc_pl': 'a',     # reiða, góða, stóra
    'dat_pl': 'um',    # reiðum, góðum, stórum
    'gen_pl': 'ra',    # reiðra, góðra, stórra
}

# Weak adjective endings - masculine (used WITH definite article)
WEAK_ADJ_ENDINGS_MASC = {
    'nom_sg': 'i',     # reiði, góði, stóri
    'acc_sg': 'a',     # reiða, góða, stóra
    'dat_sg': 'a',     # reiða, góða, stóra
    'gen_sg': 'a',     # reiða, góða, stóra
    'nom_pl': 'u',     # reiðu, góðu, stóru
    'acc_pl': 'u',     # reiðu, góðu, stóru
    'dat_pl': 'u',     # reiðu, góðu, stóru
    'gen_pl': 'u',     # reiðu, góðu, stóru
}

# Adjective stems from vocabulary (Lessons 3-9)
ADJECTIVE_STEMS = {
    # Lesson 3
    'góð':      'good',
    'ill':      'evil',
    'stór':     'big',
    'lang':     'long',
    'reið':     'angry',
    'glað':     'happy, glad',
    'svang':    'hungry',
    'hrædd':    'afraid',
    'rag':      'cowardly',
    'dauð':     'dead',
    'dansk':    'Danish',
    'norsk':    'Norwegian',
    'íslenzk':  'Icelandic',
    
    # Lesson 5
    'djúp':     'deep',
    'ung':      'young',
    'rík':      'rich',
    'heiðr':    'clear',
    'bjart':    'bright',
    'sterk':    'strong',
    'víð':      'wide',
    'breið':    'broad',
    'feig':     'doomed to die',
    'spak':     'wise',
    
    # Lesson 4
    'gyllt':    'golden',
    
    # Lesson 8
    'grœn':     'green',
    'hál':      'slippery',
    'heil':     'whole, healthy',
    'víss':     'wise',
    'gamal':    'old',
    'gul':      'yellow',
    'van':      'accustomed',
    
    # Lesson 9
    'heit':     'hot',
    'norrœn':   'Nordic',
    'vitr':     'wise',
    'alvitr':   'omniscient',
    'frjáls':   'free',
    'sjúk':     'sick',
    'blind':    'blind',
}


# =============================================================================
# LESSON 2, 3: VERB CONJUGATION
# "The form of a verb depends upon the subject in the sentence"
# =============================================================================

# Regular verb conjugation pattern (Lesson 2)
# Infinitive: [form 1], 1st person sg: [form 2]
# Pattern: ek [form 2], þú [form 2]+r, hann [form 2]+r
#          vit/vér [form 1]-a+um, þit/þér [form 1]-a+ið, þeir [form 1]

VERB_CONJUGATION = {
    # Format: infinitive -> {person: form}
    # Regular verbs from vocabulary
    
    # vega, veg - to slay (Lesson 1)
    'vega': {'inf': 'vega', '1sg': 'veg', '2sg': 'vegr', '3sg': 'vegr',
             '1pl': 'vegum', '2pl': 'vegið', '3pl': 'vega'},
    
    # heita, heiti - to be called (Lesson 1)
    'heita': {'inf': 'heita', '1sg': 'heiti', '2sg': 'heitir', '3sg': 'heitir',
              '1pl': 'heitum', '2pl': 'heitið', '3pl': 'heita'},
    
    # taka, tek - to take (Lesson 1)
    'taka': {'inf': 'taka', '1sg': 'tek', '2sg': 'tekr', '3sg': 'tekr',
             '1pl': 'tökum', '2pl': 'takið', '3pl': 'taka'},
    
    # segja, segi - to say (Lesson 1)
    'segja': {'inf': 'segja', '1sg': 'segi', '2sg': 'segir', '3sg': 'segir',
              '1pl': 'segjum', '2pl': 'segið', '3pl': 'segja'},
    
    # kalla, kalla - to call (Lesson 2)
    'kalla': {'inf': 'kalla', '1sg': 'kalla', '2sg': 'kallar', '3sg': 'kallar',
              '1pl': 'köllum', '2pl': 'kallið', '3pl': 'kalla'},
    
    # hafa, hefi - to have (Lesson 2)
    'hafa': {'inf': 'hafa', '1sg': 'hefi', '2sg': 'hefir', '3sg': 'hefir',
             '1pl': 'höfum', '2pl': 'hafið', '3pl': 'hafa'},
    
    # koma, køm - to come (Lesson 2)
    'koma': {'inf': 'koma', '1sg': 'køm', '2sg': 'kømr', '3sg': 'kømr',
             '1pl': 'komum', '2pl': 'komið', '3pl': 'koma'},
    
    # fara, fer - to go (Lesson 3)
    'fara': {'inf': 'fara', '1sg': 'fer', '2sg': 'ferr', '3sg': 'ferr',
             '1pl': 'förum', '2pl': 'farið', '3pl': 'fara'},
    
    # gefa, gef - to give (Lesson 4)
    'gefa': {'inf': 'gefa', '1sg': 'gef', '2sg': 'gefr', '3sg': 'gefr',
             '1pl': 'gefum', '2pl': 'gefið', '3pl': 'gefa'},
    
    # finna, finn - to find (Lesson 4)
    'finna': {'inf': 'finna', '1sg': 'finn', '2sg': 'finnr', '3sg': 'finnr',
              '1pl': 'finnum', '2pl': 'finnið', '3pl': 'finna'},
    
    # ganga, geng - to walk (Lesson 5)
    'ganga': {'inf': 'ganga', '1sg': 'geng', '2sg': 'gengr', '3sg': 'gengr',
              '1pl': 'göngum', '2pl': 'gangið', '3pl': 'ganga'},
    
    # standa, stend - to stand (Lesson 5)
    'standa': {'inf': 'standa', '1sg': 'stend', '2sg': 'stendr', '3sg': 'stendr',
               '1pl': 'stöndum', '2pl': 'standið', '3pl': 'standa'},
    
    # búa, bý - to live/inhabit (Lesson 5)
    'búa': {'inf': 'búa', '1sg': 'bý', '2sg': 'býr', '3sg': 'býr',
            '1pl': 'búm', '2pl': 'búið', '3pl': 'búa'},
    
    # bjóða, býð - to offer/command (Lesson 5)
    'bjóða': {'inf': 'bjóða', '1sg': 'býð', '2sg': 'býðr', '3sg': 'býðr',
              '1pl': 'bjóðum', '2pl': 'bjóðið', '3pl': 'bjóða'},
}


# Irregular verbs (Lessons 2, 3)

# vera - to be (completely irregular)
VERA_CONJUGATION = {
    'inf': 'vera',
    '1sg': 'em',   '2sg': 'ert',  '3sg': 'er',
    '1du': 'erum', '2du': 'eruð', 
    '1pl': 'erum', '2pl': 'eruð', '3pl': 'eru',
    'imp_sg': 'ver', 'imp_pl': 'verið',
}

# vilja - to want (Lesson 3)
VILJA_CONJUGATION = {
    'inf': 'vilja',
    '1sg': 'vil',   '2sg': 'vilt',  '3sg': 'vill',
    '1pl': 'viljum', '2pl': 'vilið', '3pl': 'vilja',
}

# sjá - to see (almost regular but not quite)
SJA_CONJUGATION = {
    'inf': 'sjá',
    '1sg': 'sé',   '2sg': 'sér',  '3sg': 'sér',
    '1pl': 'sjám', '2pl': 'séð',  '3pl': 'sjá',
    'imp_sg': 'sjá',
}

# =============================================================================
# LESSON 8: PRESENT-PRETERITE VERBS
# "ON has a small group of verbs that conjugate in a special way"
# =============================================================================

PRESENT_PRETERITE_VERBS = {
    # skulu - shall (Lesson 8)
    'skulu': {
        'inf': 'skulu',
        '1sg': 'skal',  '2sg': 'skalt', '3sg': 'skal',
        '1pl': 'skulum', '2pl': 'skuluð', '3pl': 'skulu',
    },
    
    # munu - will (Lesson 8)
    'munu': {
        'inf': 'munu',
        '1sg': 'mun',   '2sg': 'munt',  '3sg': 'mun',
        '1pl': 'munum', '2pl': 'munuð', '3pl': 'munu',
    },
    
    # kunna - can/know how (Lesson 8)
    'kunna': {
        'inf': 'kunna',
        '1sg': 'kann',  '2sg': 'kannt', '3sg': 'kann',
        '1pl': 'kunnum', '2pl': 'kunnuð', '3pl': 'kunnu',
    },
    
    # eiga - to own (Lesson 8)
    'eiga': {
        'inf': 'eiga',
        '1sg': 'á',     '2sg': 'átt',   '3sg': 'á',
        '1pl': 'eigum', '2pl': 'eiguð', '3pl': 'eigu',
    },
    
    # vita - to know (Lesson 9)
    'vita': {
        'inf': 'vita',
        '1sg': 'veit',  '2sg': 'veizt', '3sg': 'veit',
        '1pl': 'vitum', '2pl': 'vituð', '3pl': 'vitu',
    },
}


# =============================================================================
# LESSON 6: UMLAUTS
# =============================================================================

# I-UMLAUT (Lesson 6)
# "I-umlaut caused vowels to become fronted"
I_UMLAUT_CHANGES = {
    'a': 'e',    # hafa -> hef
    'á': 'æ',    # blása -> blæs
    'o': 'ø',    # koma -> køm
    'ó': 'œ',    # róa -> rœ
    'u': 'y',    # 
    'ú': 'ý',    # búa -> bý
    'jú': 'ý',   # bjúga -> býg
    'jó': 'ý',   # bjóða -> býð
    'au': 'ey',  # 
}

# U-UMLAUT (Lessons 2, 4, 6)
# "A u in a grammatical ending always changes a preceding 'a' to an 'ö'"
U_UMLAUT_CHANGES = {
    'a': 'ö',    # taka -> tökum, kalla -> köllum
}

# Correct umlauted forms -> incorrect non-umlauted forms
U_UMLAUT_CORRECT_TO_INCORRECT = {
    # Verb forms (1st person plural: -um ending causes umlaut)
    'tökum': 'takum',       # taka -> vit/vér tökum
    'köllum': 'kallum',     # kalla -> vit/vér köllum  
    'höfum': 'hafum',       # hafa -> vit/vér höfum
    'förum': 'farum',       # fara -> vit/vér förum
    'stöndum': 'standum',   # standa -> vit/vér stöndum
    'göngum': 'gangum',     # ganga -> vit/vér göngum
    
    # Noun dative plural forms
    'mönnum': 'mannum',     # maðr -> dat pl mönnum
    'löndum': 'landum',     # land -> dat pl löndum
    'börnum': 'barnum',     # barn -> dat pl börnum
    'körlum': 'karlum',     # karl -> dat pl körlum
    'görðum': 'garðum',     # garðr -> dat pl görðum
    'vögnum': 'vagnum',     # vagn -> dat pl vögnum
    'hröfnum': 'hrafnum',   # hrafn -> dat pl hröfnum
    'jörlum': 'jarlum',     # jarl -> dat pl jörlum
    'vöngum': 'vangum',     # vangr -> dat pl vöngum
    
    # Adjective dative forms (both sg and pl have -um)
    'glöðum': 'glaðum',     # glaðr -> dat glöðum
    'rögum': 'ragum',       # ragr -> dat rögum
    'löngum': 'langum',     # langr -> dat löngum
    'gömlum': 'gamlum',     # gamall -> dat gömlum
    
    # Pronoun dative forms
    'öllum': 'allum',       # allr -> dat öllum
    'öðrum': 'aðrum',       # annarr -> dat öðrum
}


# =============================================================================
# LESSON 4, 5, 9: QUIRKY CASE - Verbs with Dative/Genitive Objects
# =============================================================================

# Verbs that take DATIVE objects (Lessons 4, 5)
# "gefa, gef" = give, "segja, segi" = say/tell, "fœra, fœri" = bring
DATIVE_VERBS = {
    # gefa - to give (Lesson 4: "Óláfr gefr Svarti hatt")
    'gef', 'gefr', 'gefa', 'gaf', 'gáfu', 'gefi', 'gefið',
    # segja - to say/tell (Lesson 5: "Ek segi hánum at eta")
    'seg', 'segir', 'segja', 'sagði', 'sögðu', 'segi', 'segið',
    # fœra - to bring (Lesson 4: "Menninir fœra þeim góðan mat")
    'fœr', 'fœrir', 'fœra', 'fœrði', 'fœri', 'fœrið',
    'foer', 'foerir', 'foera', 'foerði', 'foeri', 'foerið',
    # bjóða - to offer/command (Lesson 5: "Ek býð hánum at eta")
    'býð', 'býðr', 'bjóða', 'bauð', 'buðu', 'bjóði',
    # sýna - to show (Lesson 5)
    'sýn', 'sýnir', 'sýna', 'sýndi', 'sýni',
    # hjálpa - to help (Lesson 8)
    'hjálp', 'hjálpar', 'hjálpa', 'hjálpaði', 'hjálpi',
    # trúa - to believe in (Lesson 9)
    'trú', 'trúir', 'trúa', 'trúði', 'trúi',
    # halda - to hold/keep (Lesson 9)
    'held', 'heldr', 'halda', 'hélt', 'héldu', 'haldi',
    # gjalda - to pay (Lesson 9)
    'geld', 'geldr', 'gjalda', 'galt', 'guldu', 'gjaldi',
    # sigla - to sail (Lesson 9)
    'sigli', 'siglir', 'sigla', 'sigldi',
    # aka - to drive (Lesson 8)
    'ek', 'ekr', 'aka', 'ók', 'óku',
}

# Verbs that take GENITIVE objects (Lesson 9)
GENITIVE_VERBS = {
    # leita - to search for (Lesson 9)
    'leita', 'leitar', 'leitaði', 'leiti',
    # sakna - to miss/feel loss of (Lesson 9)
    'sakna', 'saknar', 'saknaði', 'sakni',
}

# Dative -> Nominative transformations (for creating violations)
DATIVE_TO_NOMINATIVE = {
    'mér': 'ek', 'þér': 'þú', 
    'hánum': 'hann', 'honum': 'hann',
    'henni': 'hon', 'því': 'þat', 
    'okkr': 'vit', 'ykkr': 'þit',
    'oss': 'vér', 'yðr': 'þér', 
    'þeim': 'þeir', 'sér': 'hann',
}


# =============================================================================
# LESSON 5: PREPOSITIONS AND CASE GOVERNANCE
# "ON prepositions largely involve use of the dative case"
# =============================================================================

# Prepositions with ACCUSATIVE (allative - motion towards)
PREPOSITIONS_ACC = {
    'í':    'into',           # í + acc = into
    'á':    'onto',           # á + acc = onto
    'um':   'about, around',  # um + acc
    'við':  'by, next to',    # við + acc
}

# Prepositions with DATIVE (locative - position)
PREPOSITIONS_DAT = {
    'í':    'in(side)',       # í + dat = in
    'á':    'on (top of)',    # á + dat = on
    'ór':   'out of',         # ór + dat
    'með':  'with',           # með + dat
    'af':   'off',            # af + dat
    'yfir': 'over',           # yfir + dat
    'gegn': 'against',        # gegn + dat
    'hjá':  'by, with',       # hjá + dat
    'frá':  'from',           # frá + dat
    'undir': 'under',         # undir + dat
}

# Prepositions with GENITIVE
PREPOSITIONS_GEN = {
    'til':   'to',            # til + gen
    'meðal': 'among(st)',     # meðal + gen
}

# Prepositions that can take EITHER acc or dat with different meanings
DUAL_CASE_PREPOSITIONS = {
    'í': {'acc': 'into (motion)', 'dat': 'in (location)'},
    'á': {'acc': 'onto (motion)', 'dat': 'on (location)'},
}


# =============================================================================
# LESSON 6: WORD ORDER - V2 (Verb-Second) Rule
# "The finite verb within an Old Norse sentence must always be the first or 
#  the second component"
# =============================================================================

# V2 Rule explanation from textbook:
# "The verb is always the first or the second word in the sentence"
# 
# Valid patterns:
# - Subject-Verb-Object: "Hann sér eigi úlfinn"
# - Verb-Subject-Object: "Sér hann úlfinn eigi"
# - Object-Verb-Subject: "Úlfinn sér hann eigi"
# - Adverb-Verb-Subject: "Nú gengr úlfrinn ór skóginum"
#
# Invalid: *"Nú úlfrinn gengr ór skóginum" (verb in 3rd position)

# Conjunctions do NOT count as sentence position (Lesson 6)
# "því at menninir vilja flýja" - verb is 2nd after "menninir"
CONJUNCTIONS = {
    'ok': 'and',
    'en': 'but',
    'eða': 'or',
    'ef': 'if',
    'er': 'when',
    'því at': 'because',
    'þar er': 'where',
    'svá at': 'so that',
    'meðan': 'while',
}

# Adverbs that affect V2 (count as first position)
ADVERBS = {
    'nú': 'now',
    'þá': 'then',
    'hér': 'here',
    'þar': 'there',
    'svá': 'so',
    'eigi': 'not',
    'ok': 'also',
    'brátt': 'soon',
    'oft': 'often',
    'mjök': 'very',
    'vel': 'well',
    'heim': 'homewards',
    'aftr': 'again',
    'saman': 'together',
    'aldregi': 'never',
    'enn': 'still',
}


# =============================================================================
# LESSON 7: MIDDLE VOICE (-sk/-st suffix)
# "Reflexive/reciprocal meaning"
# =============================================================================

# Middle voice verbs -> active forms
MIDDLE_VOICE_TO_ACTIVE = {
    # -sk endings (infinitive/present)
    'kallask': 'kalla',     # to be called / call oneself
    'finnask': 'finna',     # to be found / find each other
    'hittask': 'hitta',     # to meet each other
    'settisk': 'setti',     # sat down (reflexive)
    'snúask': 'snúa',       # to turn oneself
    'berask': 'bera',       # to be carried
    'takask': 'taka',       # to be taken
    'gerask': 'gera',       # to become / be done
    'haldask': 'halda',     # to be held
    'leggjask': 'leggja',   # to lie down
    'setjask': 'setja',     # to sit down
    'berjask': 'berja',     # to fight (each other)
    'verjask': 'verja',     # to defend oneself
    
    # -st endings (3rd person)
    'kallast': 'kallar',    # is called
    'finnst': 'finnr',      # is found
    'sýnist': 'sýnir',      # seems
    
    # Past tense middle voice
    'fundusk': 'fundu',     # found each other (past)
    'hittust': 'hittu',     # met each other (past)
    'settust': 'settu',     # sat down (past pl)
    'tókusk': 'tóku',       # took each other (past)
    'gerðusk': 'gerðu',     # became (past pl)
    'börðusk': 'börðu',     # fought (past pl)
    'héldusk': 'héldu',     # held (past pl)
    'bárusk': 'báru',       # carried (past pl)
    
    # From textbook example (Lesson 4 real text)
    'stózk': 'stóð',        # stood (middle voice) - from Höfuðlausn
}

# Patterns for detecting middle voice verbs
MIDDLE_VOICE_SUFFIXES = ['sk', 'st', 'usk', 'ust', 'isk', 'ist', 'ðusk', 'ðust', 'zk', 'zt']


# =============================================================================
# LESSON 8: ASSIMILATIVE FORMS
# "Assimilation of the nominative -r to the final consonant of the stem"
# =============================================================================

# Assimilation happens with s, l, n when stem vowel is long
# *ísr -> íss, *hólr -> hóll, *steinr -> steinn

ASSIMILATIVE_ADJECTIVES = {
    # -ss (from -sr)
    'háss':   {'stem': 'hás',   'meaning': 'hoarse'},
    'víss':   {'stem': 'vís',   'meaning': 'wise'},
    
    # -ll (from -lr)  
    'háll':   {'stem': 'hál',   'meaning': 'slippery'},
    'heill':  {'stem': 'heil',  'meaning': 'whole, healthy'},
    
    # -nn (from -nr)
    'grœnn': {'stem': 'grœn',  'meaning': 'green'},
}

# Bisyllabic stems (Lesson 8)
# "Whenever there is an ending with a vowel in it, the vowel of the second 
#  stem syllable is deleted"
BISYLLABIC_NOUNS = {
    'hamarr': {'stem': 'hamar', 'syncopated': 'hamr'},  # hammer
    'himinn': {'stem': 'himin', 'syncopated': 'himn'},  # sky
    'jötunn': {'stem': 'jötun', 'syncopated': 'jötn'},  # giant
}

BISYLLABIC_ADJECTIVES = {
    'gamall': {'stem': 'gamal', 'syncopated': 'gaml'},  # old
}

BISYLLABIC_PRONOUNS = {
    'annarr': {
        'nom_sg': 'annarr', 'acc_sg': 'annan', 'dat_sg': 'öðrum', 'gen_sg': 'annars',
        'nom_pl': 'aðrir',  'acc_pl': 'aðra',  'dat_pl': 'öðrum', 'gen_pl': 'annarra',
    },
}


# =============================================================================
# LESSON 8: DEMONSTRATIVE AND INDEFINITE PRONOUNS
# =============================================================================

# Demonstrative pronoun "sá" (that, the one) - Lesson 8
SA_DECLENSION = {
    'nom_sg': 'sá',    'acc_sg': 'þann',  'dat_sg': 'þeim',  'gen_sg': 'þess',
    'nom_pl': 'þeir',  'acc_pl': 'þá',    'dat_pl': 'þeim',  'gen_pl': 'þeira',
}

# Interrogative pronoun "hverr" (who, what) - Lesson 8
HVERR_DECLENSION = {
    'nom_sg': 'hverr',  'acc_sg': 'hvern',   'dat_sg': 'hverjum', 'gen_sg': 'hvers',
    'nom_pl': 'hverir', 'acc_pl': 'hverja',  'dat_pl': 'hverjum', 'gen_pl': 'hverra',
}

# "hinn" (the other) - Lesson 8
HINN_DECLENSION = {
    'nom_sg': 'hinn',  'acc_sg': 'hinn',  'dat_sg': 'hinum', 'gen_sg': 'hins',
    'nom_pl': 'hinir', 'acc_pl': 'hina',  'dat_pl': 'hinum', 'gen_pl': 'hinna',
}

# Indefinite pronouns (Lesson 3)
INDEFINITE_PRONOUNS = {
    # allr - all, whole
    'allr': {
        'nom_sg': 'allr',  'acc_sg': 'allan', 'dat_sg': 'öllum', 'gen_sg': 'alls',
        'nom_pl': 'allir', 'acc_pl': 'alla',  'dat_pl': 'öllum', 'gen_pl': 'allra',
    },
    # margr - many
    'margr': {
        'nom_sg': 'margr',  'acc_sg': 'margan', 'dat_sg': 'mörgum', 'gen_sg': 'margs',
        'nom_pl': 'margir', 'acc_pl': 'marga',  'dat_pl': 'mörgum', 'gen_pl': 'margra',
    },
    # fáir - few (plural only)
    'fáir': {
        'nom_pl': 'fáir', 'acc_pl': 'fá',   'dat_pl': 'fám',   'gen_pl': 'fárra',
    },
    # sumir - some (plural only)
    'sumir': {
        'nom_pl': 'sumir', 'acc_pl': 'suma', 'dat_pl': 'sumum', 'gen_pl': 'sumra',
    },
    # báðir - both (plural only)
    'báðir': {
        'nom_pl': 'báðir', 'acc_pl': 'báða', 'dat_pl': 'báðum', 'gen_pl': 'beggja',
    },
}


# =============================================================================
# LESSON 4: VERB IMPERATIVE
# "Imperative forms for commands"
# =============================================================================

# Imperative formation (Lesson 4)
# Singular: stem (or stem + vowel for some verbs)
# Plural: stem + ið

VERB_IMPERATIVES = {
    # Regular verbs
    'hafa':   {'sg': 'haf',   'pl': 'hafið'},
    'kenna':  {'sg': 'kenn',  'pl': 'kennið'},
    'kalla':  {'sg': 'kalla', 'pl': 'kallið'},
    'gefa':   {'sg': 'gef',   'pl': 'gefið'},
    'taka':   {'sg': 'tak',   'pl': 'takið'},
    'fara':   {'sg': 'far',   'pl': 'farið'},
    'ganga':  {'sg': 'gakk',  'pl': 'gangið'},
    'koma':   {'sg': 'kom',   'pl': 'komið'},
    
    # Irregular
    'vera':   {'sg': 'ver',   'pl': 'verið'},
    'sjá':    {'sg': 'sjá',   'pl': 'sjáið'},
}

# =============================================================================
# LESSON 2: YES/NO QUESTIONS
# "To change a statement into a question you use the word order 
#  Verb-subject-(object/complement)"
# =============================================================================

# Question formation:
# Statement: "Hann er hér." (He is here.)
# Question: "Er hann hér?" or "Hvárt er hann hér?" (Is he here?)

QUESTION_PARTICLES = {'hvárt', 'hvat', 'hverr', 'hví', 'hvar', 'hvaðan'}


# =============================================================================
# VOCABULARY: COMPLETE WORD LISTS FROM LESSONS 1-9
# =============================================================================

# All nouns from the textbook
NOUNS_VOCABULARY = {
    # Lesson 1 - Strong masculine
    'álfr': 'elf', 'baugr': 'ring', 'brandr': 'sword', 'dvergr': 'dwarf',
    'draugr': 'ghost', 'hestr': 'horse', 'haukr': 'hawk', 'hjálmr': 'helmet',
    'konungr': 'king', 'knífr': 'knife', 'ormr': 'worm, serpent', 'úlfr': 'wolf',
    
    # Lesson 2
    'maðr': 'person, man', 'Norðmaðr': 'Norwegian', 'hrafn': 'raven',
    'jarl': 'earl', 'bátr': 'boat', 'geirr': 'spear', 'Íslendingr': 'Icelander',
    'vargr': 'wolf', 'víkingr': 'viking', 'þjófr': 'thief',
    
    # Lesson 3
    'matr': 'food', 'fiskr': 'fish', 'ostr': 'cheese',
    
    # Lesson 4
    'hattr': 'hat', 'grautr': 'porridge',
    
    # Lesson 5
    'skógr': 'forest', 'vágr': 'small bay, cove', 'hólmr': 'isle',
    'garðr': 'palisade, city, garden', 'haugr': 'mound, grave',
    'eldr': 'fire', 'vindr': 'wind', 'vangr': 'field, meadow',
    'brunnr': 'well', 'heimr': 'home, world', 'oddr': 'point, spike',
    'fors': 'waterfall', 'sandr': 'sand',
    
    # Lesson 8
    'áss': 'god (Æsir)', 'íss': 'ice', 'þræll': 'slave', 'vagn': 'wagon',
    'hamarr': 'hammer', 'himinn': 'sky', 'jötunn': 'giant',
    'drottinn': 'lord', 'hringr': 'ring', 'hundr': 'dog',
    'níðingr': 'villain', 'viðr': 'wood',
    
    # Lesson 9
    'vinr': 'friend', 'askr': 'ash tree', 'sveinn': 'young man',
    'peningr': 'money', 'máttr': 'power', 'kaupmaðr': 'merchant',
    'dómr': 'judgement', 'þrældómr': 'slavery',
}

# All verbs from the textbook
VERBS_VOCABULARY = {
    # Lesson 1
    'á': 'owns', 'er': 'is', 'heitir': 'is called', 'sér': 'sees',
    'segir': 'says', 'tekr': 'takes', 'vegr': 'kills, slays',
    
    # Lesson 2
    'hafa': 'have, hold, wear', 'hata': 'hate', 'heita': 'be called',
    'deyja': 'die', 'bíða': 'wait', 'koma': 'come', 'mæla': 'talk',
    'sjá': 'see', 'vega': 'slay', 'segja': 'say', 'taka': 'take',
    'vera': 'be',
    
    # Lesson 3
    'eta': 'eat', 'veiða': 'hunt, fish', 'flýja': 'flee',
    'spyrja': 'ask', 'svara': 'answer', 'kenna': 'recognize, know',
    'elta': 'follow, chase', 'heyra': 'hear', 'fara': 'go', 'vilja': 'want',
    
    # Lesson 4
    'gefa': 'give', 'fœra': 'bring', 'finna': 'find', 'hlæja': 'laugh',
    
    # Lesson 5
    'sigla': 'sail', 'ganga': 'walk', 'bjóða': 'offer, command',
    'sýna': 'show', 'búa': 'live, inhabit', 'brenna': 'be burning',
    'blása': 'blow', 'falla': 'fall', 'skína': 'shine',
    'standa': 'stand', 'lifa': 'live',
    
    # Lesson 8
    'gjøra': 'do', 'aka': 'drive', 'hringa': 'wind around',
    'hjálpa': 'help', 'róa': 'row', 'leiða': 'lead',
    'vernda': 'protect', 'reka': 'drive out', 'verða': 'become',
    'skulu': 'shall', 'munu': 'will', 'kunna': 'can, know how',
    'eiga': 'own',
    
    # Lesson 9
    'smíða': 'craft, make', 'trúa': 'believe in', 'leita': 'search for',
    'kaupa': 'buy', 'halda': 'hold, keep', 'velja': 'choose',
    'gjalda': 'pay', 'rísa': 'rise', 'lækna': 'heal', 'vita': 'know',
}


# =============================================================================
# PROPER NAMES FROM THE TEXTBOOK
# =============================================================================

# Personal names (Lessons 1-9)
PERSONAL_NAMES = {
    'Haukr', 'Óláfr', 'Sigurðr', 'Tyrfingr', 'Eiríkr', 'Erlingr',
    'Svartr', 'Kormákr', 'Einarr', 'Fjalarr', 'Gandálfr', 'Ragnarr',
    'Hjálmarr', 'Oddr', 'Úlfarr', 'Þórr', 'Óðinn', 'Baldr',
    'Kristr', 'Surtr', 'Njáll', 'Haraldr', 'Þorvarðr',
}

# Place names with meanings
PLACE_NAMES = {
    'Noregr': 'Norway',
    'Ísland': 'Iceland',
    'Danmörk': 'Denmark',
    'Geirshólmr': "Geir's Isle",
    'Geirshaugr': "Geir's Grave",
    'Heiðvangr': 'Clear Field',
    'Skógarfors': "Forest's Falls",
    'Úlfarsheimr': "Úlfar's Home",
    'Hólmgarðr': 'Island City (Novgorod)',
    'Austrvegr': 'Eastway (Russia)',
    'Vestrvegr': 'Westway (British Isles)',
    # Mythological places
    'Ásgarðr': 'Asgard (world of gods)',
    'Miðgarðr': 'Midgard (world of men)',
    'Jötunheimr': 'Gianthome',
    'Útgarðr': 'Outgard',
    'Múspellsheimr': 'Muspellsheim (World of Fire Giants)',
}

# =============================================================================
# SAMPLE SENTENCES FROM THE TEXTBOOK
# =============================================================================

SAMPLE_SENTENCES = [
    # Lesson 1
    "Vegr orminn Óláfr.",
    "Baug á dvergr.",
    "Draugrinn sér konunginn.",
    "Heitir konungrinn Óláfr.",
    
    # Lesson 2
    "Norðmenn hata Íslendinga.",
    "Hatar konungrinn úlfa.",
    "Þeir eru Norðmenn.",
    "Brandrinn, er hann á, heitir Tyrfingr.",
    "Vit höfum hjálma.",
    
    # Lesson 3
    "Hér eru reiðir menn.",
    "Hann sér reiðan mann.",
    "Óláfr er maðr reiðr.",
    "Ek sé Óláf konung koma.",
    "Konungrinn vill vega mennina.",
    
    # Lesson 4
    "Svartr gefr Kormáki fiska.",
    "Menninir fœra þeim góðan mat.",
    "Konungrinn fœrir Norðmönnunum knífa ok geira.",
    
    # Lesson 5
    "Úlfrinn gengr í skóginn.",
    "Úlfrinn gengr í skóginum.",
    "Eldr mjök bjartr brennr í garðinum.",
    "Ragnarr ferr með víkingum í váginn.",
    
    # Lesson 8
    "Þeir ganga saman um víðan vang.",
    "Þeir sjá menn standa við forsinn.",
    "Jarlar Noregs eigu marga hunda ok þræla írska.",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_pronoun_case(pronoun: str) -> Optional[str]:
    """Determine the case of a pronoun."""
    pronoun_lower = pronoun.lower()
    if pronoun_lower in NOMINATIVE_PRONOUNS:
        return 'nom'
    elif pronoun_lower in ACCUSATIVE_PRONOUNS:
        return 'acc'
    elif pronoun_lower in DATIVE_PRONOUNS:
        return 'dat'
    elif pronoun_lower in GENITIVE_PRONOUNS:
        return 'gen'
    elif pronoun_lower in REFLEXIVE_PRONOUNS:
        return REFLEXIVE_PRONOUNS[pronoun_lower]
    return None


def transform_pronoun_case(pronoun: str, target_case: str) -> Optional[str]:
    """Transform a pronoun to a different case."""
    pronoun_lower = pronoun.lower()
    if pronoun_lower in PRONOUN_DECLENSION:
        return PRONOUN_DECLENSION[pronoun_lower].get(target_case)
    return None


def apply_u_umlaut(word: str) -> str:
    """Apply u-umlaut: a -> ö before -um endings."""
    if word.endswith('um'):
        # Find the last 'a' before the ending and change to 'ö'
        stem = word[:-2]
        if 'a' in stem:
            # Replace last 'a' with 'ö'
            idx = stem.rfind('a')
            stem = stem[:idx] + 'ö' + stem[idx+1:]
        return stem + 'um'
    return word


def remove_u_umlaut(word: str) -> str:
    """Remove u-umlaut: ö -> a (creates ungrammatical form)."""
    if word.endswith('um') and 'ö' in word:
        return word.replace('ö', 'a')
    return word


def is_middle_voice(word: str) -> bool:
    """Check if a word is in middle voice."""
    for suffix in MIDDLE_VOICE_SUFFIXES:
        if word.endswith(suffix):
            return True
    return False


def get_strong_adj_form(stem: str, case: str, number: str) -> str:
    """Get strong (indefinite) adjective form."""
    key = f"{case}_{number}"
    ending = STRONG_ADJ_ENDINGS_MASC.get(key, '')
    return stem + ending


def get_weak_adj_form(stem: str, case: str, number: str) -> str:
    """Get weak (definite) adjective form."""
    key = f"{case}_{number}"
    ending = WEAK_ADJ_ENDINGS_MASC.get(key, '')
    return stem + ending


def decline_strong_masc_noun(noun_info: dict, case: str, number: str, 
                              with_article: bool = False) -> str:
    """Decline a strong masculine noun."""
    stem = noun_info['stem']
    
    if number == 'sg':
        if case == 'nom':
            form = stem + 'r' if noun_info['type'] not in ['no-r', 'assimilative'] else stem
            if noun_info['type'] == 'assimilative':
                # Double the final consonant
                form = stem + stem[-1]
        elif case == 'acc':
            form = stem
        elif case == 'dat':
            form = stem + 'i'
        elif case == 'gen':
            form = noun_info['gen_sg'].replace(stem, '') 
            form = stem + form if not noun_info['gen_sg'].startswith(stem) else noun_info['gen_sg']
    else:  # plural
        if case == 'nom':
            form = noun_info['nom_pl']
        elif case == 'acc':
            form = stem + 'a'
        elif case == 'dat':
            form = apply_u_umlaut(stem + 'um')
        elif case == 'gen':
            form = stem + 'a'
    
    if with_article:
        article = MASCULINE_ARTICLE[f"{case}_{number}"]
        form = attach_article(form, article)
    
    return form


# =============================================================================
# CORPUS LOADING
# =============================================================================

def load_corpus() -> List[str]:
    """Load sentences from norsecorpus package."""
    if not HAS_CORPUS:
        return SAMPLE_SENTENCES
    
    sentences = []
    try:
        available_texts = ncr.get_available_texts()
        
        for filename in available_texts:
            try:
                text_data = ncr.read_tei_words(available_texts[filename])
                for chapter in text_data:
                    for paragraph in chapter:
                        for sentence in paragraph:
                            if isinstance(sentence, list) and len(sentence) > 0:
                                sent_text = ' '.join(sentence)
                                if sent_text.strip():
                                    sentences.append(sent_text)
            except Exception:
                continue
    except Exception:
        return SAMPLE_SENTENCES
    
    return sentences if sentences else SAMPLE_SENTENCES


def filter_sentences(sentences: List[str], min_words: int = 5, 
                     max_words: int = 25) -> List[str]:
    """Filter sentences to those usable for minimal pair generation."""
    usable = []
    for sent in sentences:
        words = sent.split()
        if len(words) < min_words or len(words) > max_words:
            continue
        # Must end with punctuation
        if not any(sent.strip().endswith(p) for p in '.?!'):
            continue
        # Skip if too many punctuation marks (likely poetry/fragments)
        punct_count = sum(1 for c in sent if c in '.,;:!?')
        if punct_count > 4:
            continue
        usable.append(sent)
    return usable


# =============================================================================
# MINIMAL PAIR GENERATION FUNCTIONS
# =============================================================================

def generate_case_violation(sentence: str) -> Optional[MinimalPair]:
    """Generate a minimal pair by violating pronoun case agreement."""
    words = sentence.split()
    
    for i, word in enumerate(words):
        word_lower = word.lower().rstrip('.,;:!?')
        
        # Check if it's a dative pronoun after a dative verb
        if word_lower in DATIVE_PRONOUNS:
            # Check if previous word is a dative verb
            if i > 0:
                prev_word = words[i-1].lower().rstrip('.,;:!?')
                if prev_word in DATIVE_VERBS:
                    # Create violation by using nominative instead
                    if word_lower in DATIVE_TO_NOMINATIVE:
                        wrong_form = DATIVE_TO_NOMINATIVE[word_lower]
                        punct = word[len(word_lower):] if len(word) > len(word_lower) else ''
                        
                        ungrammatical_words = words.copy()
                        ungrammatical_words[i] = wrong_form + punct
                        
                        return MinimalPair(
                            id=f"case_{hash(sentence) % 10000}",
                            phenomenon="quirky_case_dative",
                            grammatical=sentence,
                            ungrammatical=' '.join(ungrammatical_words),
                            target=word_lower,
                            error_type="dative_to_nominative"
                        )
    return None


def generate_umlaut_violation(sentence: str) -> Optional[MinimalPair]:
    """Generate a minimal pair by removing u-umlaut."""
    words = sentence.split()
    
    for i, word in enumerate(words):
        word_clean = word.lower().rstrip('.,;:!?')
        
        if word_clean in U_UMLAUT_CORRECT_TO_INCORRECT:
            wrong_form = U_UMLAUT_CORRECT_TO_INCORRECT[word_clean]
            punct = word[len(word_clean):] if len(word) > len(word_clean) else ''
            
            # Preserve original capitalization
            if word[0].isupper():
                wrong_form = wrong_form.capitalize()
            
            ungrammatical_words = words.copy()
            ungrammatical_words[i] = wrong_form + punct
            
            return MinimalPair(
                id=f"umlaut_{hash(sentence) % 10000}",
                phenomenon="u_umlaut",
                grammatical=sentence,
                ungrammatical=' '.join(ungrammatical_words),
                target=word_clean,
                error_type="missing_u_umlaut"
            )
    return None


def generate_middle_voice_violation(sentence: str) -> Optional[MinimalPair]:
    """Generate a minimal pair by removing middle voice suffix."""
    words = sentence.split()
    
    for i, word in enumerate(words):
        word_clean = word.lower().rstrip('.,;:!?')
        
        if word_clean in MIDDLE_VOICE_TO_ACTIVE:
            wrong_form = MIDDLE_VOICE_TO_ACTIVE[word_clean]
            punct = word[len(word_clean):] if len(word) > len(word_clean) else ''
            
            if word[0].isupper():
                wrong_form = wrong_form.capitalize()
            
            ungrammatical_words = words.copy()
            ungrammatical_words[i] = wrong_form + punct
            
            return MinimalPair(
                id=f"middle_{hash(sentence) % 10000}",
                phenomenon="middle_voice",
                grammatical=sentence,
                ungrammatical=' '.join(ungrammatical_words),
                target=word_clean,
                error_type="missing_middle_voice"
            )
    return None


def generate_adjective_violation(sentence: str) -> Optional[MinimalPair]:
    """Generate a minimal pair by using wrong adjective declension."""
    words = sentence.split()
    
    for i, word in enumerate(words):
        word_clean = word.lower().rstrip('.,;:!?')
        
        # Check for strong adjective forms that should be weak (or vice versa)
        for stem in ADJECTIVE_STEMS:
            # Strong nom sg -> weak nom sg
            if word_clean == stem + 'r':
                wrong_form = stem + 'i'  # weak form
                punct = word[len(word_clean):] if len(word) > len(word_clean) else ''
                
                if word[0].isupper():
                    wrong_form = wrong_form.capitalize()
                
                ungrammatical_words = words.copy()
                ungrammatical_words[i] = wrong_form + punct
                
                return MinimalPair(
                    id=f"adj_{hash(sentence) % 10000}",
                    phenomenon="adjective_declension",
                    grammatical=sentence,
                    ungrammatical=' '.join(ungrammatical_words),
                    target=word_clean,
                    error_type="strong_to_weak"
                )
            
            # Strong acc sg -> wrong ending
            if word_clean == stem + 'an':
                wrong_form = stem + 'a'  # weak form
                punct = word[len(word_clean):] if len(word) > len(word_clean) else ''
                
                if word[0].isupper():
                    wrong_form = wrong_form.capitalize()
                
                ungrammatical_words = words.copy()
                ungrammatical_words[i] = wrong_form + punct
                
                return MinimalPair(
                    id=f"adj_{hash(sentence) % 10000}",
                    phenomenon="adjective_declension",
                    grammatical=sentence,
                    ungrammatical=' '.join(ungrammatical_words),
                    target=word_clean,
                    error_type="strong_to_weak_acc"
                )
    return None


def generate_verb_agreement_violation(sentence: str) -> Optional[MinimalPair]:
    """Generate a minimal pair by violating subject-verb agreement."""
    words = sentence.split()
    
    # Look for verb forms and check agreement
    for verb_inf, forms in VERB_CONJUGATION.items():
        for i, word in enumerate(words):
            word_clean = word.lower().rstrip('.,;:!?')
            
            # If we find a 3sg form, try to make it 1sg (wrong agreement)
            if word_clean == forms['3sg']:
                # Check if subject is 3rd person
                if i > 0:
                    prev = words[i-1].lower().rstrip('.,;:!?')
                    if prev in {'hann', 'hon', 'þat'} or prev.endswith('inn') or prev.endswith('r'):
                        wrong_form = forms['1sg']
                        punct = word[len(word_clean):] if len(word) > len(word_clean) else ''
                        
                        ungrammatical_words = words.copy()
                        ungrammatical_words[i] = wrong_form + punct
                        
                        return MinimalPair(
                            id=f"verb_{hash(sentence) % 10000}",
                            phenomenon="verb_agreement",
                            grammatical=sentence,
                            ungrammatical=' '.join(ungrammatical_words),
                            target=word_clean,
                            error_type="person_mismatch"
                        )
    return None


def generate_all_minimal_pairs(sentences: List[str]) -> List[MinimalPair]:
    """Generate all types of minimal pairs from sentences."""
    pairs = []
    
    generators = [
        generate_case_violation,
        generate_umlaut_violation,
        generate_middle_voice_violation,
        generate_adjective_violation,
        generate_verb_agreement_violation,
    ]
    
    for sent in sentences:
        for generator in generators:
            pair = generator(sent)
            if pair:
                pairs.append(pair)
    
    return pairs


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to demonstrate grammar rules."""
    print("Old Norse Grammar Rules - Based on 'Old Norse for Beginners'")
    print("=" * 60)
    
    print(f"\n1. PRONOUNS:")
    print(f"   Nominative: {len(NOMINATIVE_PRONOUNS)} forms")
    print(f"   Accusative: {len(ACCUSATIVE_PRONOUNS)} forms")
    print(f"   Dative: {len(DATIVE_PRONOUNS)} forms")
    print(f"   Genitive: {len(GENITIVE_PRONOUNS)} forms")
    
    print(f"\n2. NOUNS:")
    print(f"   Strong masculine nouns: {len(STRONG_MASCULINE_NOUNS)}")
    print(f"   Vocabulary nouns: {len(NOUNS_VOCABULARY)}")
    
    print(f"\n3. ADJECTIVES:")
    print(f"   Adjective stems: {len(ADJECTIVE_STEMS)}")
    
    print(f"\n4. VERBS:")
    print(f"   Regular conjugations: {len(VERB_CONJUGATION)}")
    print(f"   Present-preterite verbs: {len(PRESENT_PRETERITE_VERBS)}")
    print(f"   Dative verbs: {len(DATIVE_VERBS)}")
    
    print(f"\n5. U-UMLAUT PAIRS:")
    print(f"   Correct -> Incorrect mappings: {len(U_UMLAUT_CORRECT_TO_INCORRECT)}")
    
    print(f"\n6. MIDDLE VOICE:")
    print(f"   Middle -> Active mappings: {len(MIDDLE_VOICE_TO_ACTIVE)}")
    
    print(f"\n7. PREPOSITIONS:")
    print(f"   With accusative: {len(PREPOSITIONS_ACC)}")
    print(f"   With dative: {len(PREPOSITIONS_DAT)}")
    print(f"   With genitive: {len(PREPOSITIONS_GEN)}")
    
    # Load and process corpus
    print("\n" + "=" * 60)
    print("Loading corpus...")
    sentences = load_corpus()
    filtered = filter_sentences(sentences)
    print(f"Total sentences: {len(sentences)}")
    print(f"Filtered sentences: {len(filtered)}")
    
    # Generate minimal pairs
    print("\nGenerating minimal pairs...")
    pairs = generate_all_minimal_pairs(filtered[:100])  # Limit for demo
    print(f"Generated {len(pairs)} minimal pairs")
    
    # Show examples
    if pairs:
        print("\nExample minimal pairs:")
        for pair in pairs[:5]:
            print(f"\n  Phenomenon: {pair.phenomenon}")
            print(f"  Grammatical: {pair.grammatical}")
            print(f"  Ungrammatical: {pair.ungrammatical}")
            print(f"  Target: {pair.target}")


if __name__ == "__main__":
    main()
