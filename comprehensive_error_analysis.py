"""
Comprehensive analysis of ALL errors with statistical validation.
"""

import pandas as pd
import numpy as np
from scipy import stats
import re
import os

def load_all_results():
    """Load all evaluation results."""
    models = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b", 
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    
    dfs = []
    for model in models:
        filename = f"evaluation_results_{model.replace('/', '_')}.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename, encoding='utf-8-sig')
            dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)

def analyze_middle_voice_comprehensive(df):
    """Comprehensive analysis of ALL middle voice errors."""
    print("=== COMPREHENSIVE MIDDLE VOICE ANALYSIS ===\n")
    
    middle_voice = df[df['phenomenon'] == 'MIDDLE_VOICE']
    
    # Pattern analysis for ALL errors
    results = {}
    
    for model in middle_voice['model'].unique():
        model_data = middle_voice[middle_voice['model'] == model]
        errors = model_data[model_data['correct'] == False]
        
        # Analyze ALL error patterns
        sk_suffix_errors = 0
        st_suffix_errors = 0
        other_errors = 0
        
        sk_examples = []
        st_examples = []
        
        for _, row in errors.iterrows():
            gram = row['grammatical']
            ungram = row['ungrammatical']
            
            # Check for -sk suffix pattern
            if re.search(r'\w+sk\b', gram) and not re.search(r'\w+sk\b', ungram):
                sk_suffix_errors += 1
                sk_examples.append((gram, ungram))
            # Check for -st suffix pattern  
            elif re.search(r'\w+st\b', gram) and not re.search(r'\w+st\b', ungram):
                st_suffix_errors += 1
                st_examples.append((gram, ungram))
            else:
                other_errors += 1
        
        results[model] = {
            'total_errors': len(errors),
            'total_pairs': len(model_data),
            'accuracy': model_data['correct'].mean(),
            'sk_errors': sk_suffix_errors,
            'st_errors': st_suffix_errors,
            'other_errors': other_errors,
            'sk_examples': sk_examples[:3],  # First 3 examples
            'st_examples': st_examples[:3]
        }
    
    # Print comprehensive results
    for model, data in results.items():
        print(f"{model}:")
        print(f"  Accuracy: {data['accuracy']:.3f} ({data['total_errors']}/{data['total_pairs']} errors)")
        print(f"  -sk suffix errors: {data['sk_errors']} ({data['sk_errors']/data['total_errors']*100:.1f}% of errors)")
        print(f"  -st suffix errors: {data['st_errors']} ({data['st_errors']/data['total_errors']*100:.1f}% of errors)")
        print(f"  Other errors: {data['other_errors']} ({data['other_errors']/data['total_errors']*100:.1f}% of errors)")
        
        if data['sk_examples']:
            print(f"  -sk examples:")
            for i, (gram, ungram) in enumerate(data['sk_examples']):
                print(f"    {i+1}. '{gram[:50]}...' vs '{ungram[:50]}...'")
        print()
    
    return results

def analyze_umlaut_comprehensive(df):
    """Comprehensive analysis of ALL u-umlaut errors."""
    print("=== COMPREHENSIVE U-UMLAUT ANALYSIS ===\n")
    
    umlaut = df[df['phenomenon'] == 'UMLAUT']
    
    results = {}
    
    for model in umlaut['model'].unique():
        model_data = umlaut[umlaut['model'] == model]
        errors = model_data[model_data['correct'] == False]
        
        # Analyze ALL pairs for ǫ character
        o_ogonek_pairs = 0
        o_ogonek_errors = 0
        a_to_o_errors = 0
        other_vowel_errors = 0
        
        o_ogonek_examples = []
        
        for _, row in model_data.iterrows():
            gram = row['grammatical']
            ungram = row['ungrammatical']
            is_error = not row['correct']
            
            # Check for ǫ character
            if 'ǫ' in gram or 'ǫ' in ungram:
                o_ogonek_pairs += 1
                if is_error:
                    o_ogonek_errors += 1
                    o_ogonek_examples.append((gram, ungram))
            
            # Check for a→ǫ pattern
            if is_error:
                if 'ǫ' in gram and 'a' in ungram:
                    a_to_o_errors += 1
                elif re.search(r'[aeiou]', gram) and re.search(r'[aeiou]', ungram):
                    other_vowel_errors += 1
        
        results[model] = {
            'total_errors': len(errors),
            'total_pairs': len(model_data),
            'accuracy': model_data['correct'].mean(),
            'o_ogonek_pairs': o_ogonek_pairs,
            'o_ogonek_errors': o_ogonek_errors,
            'o_ogonek_accuracy': (o_ogonek_pairs - o_ogonek_errors) / o_ogonek_pairs if o_ogonek_pairs > 0 else 0,
            'a_to_o_errors': a_to_o_errors,
            'other_vowel_errors': other_vowel_errors,
            'examples': o_ogonek_examples[:3]
        }
    
    # Print results
    for model, data in results.items():
        print(f"{model}:")
        print(f"  Overall accuracy: {data['accuracy']:.3f}")
        print(f"  ǫ character pairs: {data['o_ogonek_pairs']}/{data['total_pairs']} ({data['o_ogonek_pairs']/data['total_pairs']*100:.1f}%)")
        if data['o_ogonek_pairs'] > 0:
            print(f"  ǫ accuracy: {data['o_ogonek_accuracy']:.3f} ({data['o_ogonek_errors']}/{data['o_ogonek_pairs']} errors)")
        print(f"  a→ǫ errors: {data['a_to_o_errors']}")
        print()
    
    return results

def analyze_quirky_case_comprehensive(df):
    """Comprehensive analysis of ALL quirky case errors."""
    print("=== COMPREHENSIVE QUIRKY CASE ANALYSIS ===\n")
    
    quirky = df[df['phenomenon'] == 'QUIRKY_CASE']
    
    results = {}
    
    for model in quirky['model'].unique():
        model_data = quirky[quirky['model'] == model]
        errors = model_data[model_data['correct'] == False]
        
        # Analyze dative vs nominative patterns
        dative_to_nom_errors = 0
        other_case_errors = 0
        
        dative_pronouns = ['honum', 'henni', 'því', 'þeim', 'okkr', 'ykkr']
        nominative_pronouns = ['hann', 'hon', 'þat', 'þeir', 'vit', 'þit']
        
        for _, row in errors.iterrows():
            gram = row['grammatical']
            ungram = row['ungrammatical']
            
            # Check for dative→nominative error
            found_dative_to_nom = False
            for dat, nom in zip(dative_pronouns, nominative_pronouns):
                if dat in gram.lower() and nom in ungram.lower():
                    dative_to_nom_errors += 1
                    found_dative_to_nom = True
                    break
            
            if not found_dative_to_nom:
                other_case_errors += 1
        
        results[model] = {
            'total_errors': len(errors),
            'total_pairs': len(model_data),
            'accuracy': model_data['correct'].mean(),
            'dative_to_nom_errors': dative_to_nom_errors,
            'other_case_errors': other_case_errors
        }
    
    # Print results
    for model, data in results.items():
        print(f"{model}:")
        print(f"  Accuracy: {data['accuracy']:.3f} ({data['total_errors']}/{data['total_pairs']} errors)")
        if data['total_errors'] > 0:
            print(f"  Dative→Nominative errors: {data['dative_to_nom_errors']} ({data['dative_to_nom_errors']/data['total_errors']*100:.1f}% of errors)")
            print(f"  Other case errors: {data['other_case_errors']} ({data['other_case_errors']/data['total_errors']*100:.1f}% of errors)")
        print()
    
    return results

def analyze_adjective_comprehensive(df):
    """Comprehensive analysis of ALL adjective errors."""
    print("=== COMPREHENSIVE ADJECTIVE ANALYSIS ===\n")
    
    adjective = df[df['phenomenon'] == 'ADJECTIVE']
    
    results = {}
    
    for model in adjective['model'].unique():
        model_data = adjective[adjective['model'] == model]
        errors = model_data[model_data['correct'] == False]
        
        # Analyze strong vs weak patterns
        strong_to_weak_errors = 0
        weak_to_strong_errors = 0
        other_errors = 0
        
        # Common strong/weak endings
        strong_endings = ['r', 'll', 'nn', 'tt']
        weak_endings = ['i', 'a', 'u']
        
        for _, row in errors.iterrows():
            gram = row['grammatical']
            ungram = row['ungrammatical']
            
            # Simple heuristic for strong/weak detection
            has_strong_gram = any(gram.endswith(ending) for ending in strong_endings)
            has_weak_gram = any(gram.endswith(ending) for ending in weak_endings)
            has_strong_ungram = any(ungram.endswith(ending) for ending in strong_endings)
            has_weak_ungram = any(ungram.endswith(ending) for ending in weak_endings)
            
            if has_strong_gram and has_weak_ungram:
                strong_to_weak_errors += 1
            elif has_weak_gram and has_strong_ungram:
                weak_to_strong_errors += 1
            else:
                other_errors += 1
        
        results[model] = {
            'total_errors': len(errors),
            'total_pairs': len(model_data),
            'accuracy': model_data['correct'].mean(),
            'strong_to_weak_errors': strong_to_weak_errors,
            'weak_to_strong_errors': weak_to_strong_errors,
            'other_errors': other_errors
        }
    
    # Print results
    for model, data in results.items():
        print(f"{model}:")
        print(f"  Accuracy: {data['accuracy']:.3f} ({data['total_errors']}/{data['total_pairs']} errors)")
        if data['total_errors'] > 0:
            print(f"  Strong→Weak errors: {data['strong_to_weak_errors']} ({data['strong_to_weak_errors']/data['total_errors']*100:.1f}% of errors)")
            print(f"  Weak→Strong errors: {data['weak_to_strong_errors']} ({data['weak_to_strong_errors']/data['total_errors']*100:.1f}% of errors)")
            print(f"  Other errors: {data['other_errors']} ({data['other_errors']/data['total_errors']*100:.1f}% of errors)")
        print()
    
    return results

def analyze_response_patterns_comprehensive(df):
    """Comprehensive analysis of response patterns."""
    print("=== COMPREHENSIVE RESPONSE PATTERN ANALYSIS ===\n")
    
    # 1. Choice bias analysis
    print("1. Choice Bias Analysis (A vs B preference):")
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        a_count = (model_data['choice'] == 'A').sum()
        b_count = (model_data['choice'] == 'B').sum()
        total = len(model_data)
        
        a_pct = a_count / total * 100
        b_pct = b_count / total * 100
        
        # Chi-square test for bias
        expected = total / 2
        chi2 = ((a_count - expected)**2 + (b_count - expected)**2) / expected
        p_value = 1 - stats.chi2.cdf(chi2, 1)
        
        print(f"  {model}:")
        print(f"    A: {a_count} ({a_pct:.1f}%), B: {b_count} ({b_pct:.1f}%)")
        print(f"    Chi-square test: χ²={chi2:.3f}, p={p_value:.6f}")
        if p_value < 0.001:
            print(f"    *** Highly significant bias towards {'A' if a_count > b_count else 'B'}")
        elif p_value < 0.05:
            print(f"    ** Significant bias towards {'A' if a_count > b_count else 'B'}")
        print()
    
    # 2. Order effect analysis
    print("2. Order Effect Analysis (A_gram vs B_gram):")
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        a_gram_data = model_data[model_data['order'] == 'A_gram']
        b_gram_data = model_data[model_data['order'] == 'B_gram']
        
        a_gram_acc = a_gram_data['correct'].mean()
        b_gram_acc = b_gram_data['correct'].mean()
        
        # T-test for order effect
        t_stat, p_value = stats.ttest_ind(a_gram_data['correct'], b_gram_data['correct'])
        
        print(f"  {model}:")
        print(f"    A_gram accuracy: {a_gram_acc:.3f} (n={len(a_gram_data)})")
        print(f"    B_gram accuracy: {b_gram_acc:.3f} (n={len(b_gram_data)})")
        print(f"    Difference: {abs(a_gram_acc - b_gram_acc):.3f}")
        print(f"    T-test: t={t_stat:.3f}, p={p_value:.6f}")
        if p_value < 0.05:
            print(f"    ** Significant order effect")
        print()

def statistical_validation(df):
    """Statistical validation of key claims."""
    print("=== STATISTICAL VALIDATION OF CLAIMS ===\n")
    
    # Claim 1: Middle voice is hardest phenomenon
    print("1. Claim: Middle voice is the hardest phenomenon")
    phen_acc = df.groupby('phenomenon')['correct'].mean().sort_values()
    print(f"   Phenomenon difficulty ranking:")
    for i, (phen, acc) in enumerate(phen_acc.items()):
        print(f"   {i+1}. {phen}: {acc:.3f}")
    
    middle_voice_acc = phen_acc['MIDDLE_VOICE']
    is_hardest = middle_voice_acc == phen_acc.min()
    print(f"   MIDDLE_VOICE accuracy: {middle_voice_acc:.3f}")
    print(f"   Is hardest: {is_hardest} ✓" if is_hardest else f"   Is hardest: {is_hardest} ✗")
    
    # Claim 2: OpenAI models fail at middle voice
    print(f"\n2. Claim: OpenAI models particularly struggle with middle voice")
    middle_voice = df[df['phenomenon'] == 'MIDDLE_VOICE']
    
    openai_models = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b']
    llama_models = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant']
    
    openai_acc = middle_voice[middle_voice['model'].isin(openai_models)]['correct'].mean()
    llama_acc = middle_voice[middle_voice['model'].isin(llama_models)]['correct'].mean()
    
    print(f"   OpenAI average on MIDDLE_VOICE: {openai_acc:.3f}")
    print(f"   Llama average on MIDDLE_VOICE: {llama_acc:.3f}")
    print(f"   Difference: {llama_acc - openai_acc:.3f}")
    
    # Statistical test
    openai_data = middle_voice[middle_voice['model'].isin(openai_models)]['correct']
    llama_data = middle_voice[middle_voice['model'].isin(llama_models)]['correct']
    t_stat, p_value = stats.ttest_ind(openai_data, llama_data)
    print(f"   T-test: t={t_stat:.3f}, p={p_value:.6f}")
    if p_value < 0.001:
        print(f"   *** Highly significant difference ✓")
    
    # Claim 3: Model size vs architecture
    print(f"\n3. Claim: Architecture matters more than size")
    print(f"   llama-3.3-70b (70B): {df[df['model'] == 'llama-3.3-70b-versatile']['correct'].mean():.3f}")
    print(f"   openai/gpt-oss-120b (120B): {df[df['model'] == 'openai/gpt-oss-120b']['correct'].mean():.3f}")
    
    smaller_better = df[df['model'] == 'llama-3.3-70b-versatile']['correct'].mean() > df[df['model'] == 'openai/gpt-oss-120b']['correct'].mean()
    print(f"   Smaller Llama > Larger OpenAI: {smaller_better} {'✓' if smaller_better else '✗'}")

def main():
    print("COMPREHENSIVE ERROR ANALYSIS WITH STATISTICAL VALIDATION")
    print("=" * 80)
    
    df = load_all_results()
    print(f"Analyzing {len(df)} total evaluations\n")
    
    # Comprehensive analyses
    middle_results = analyze_middle_voice_comprehensive(df)
    umlaut_results = analyze_umlaut_comprehensive(df)
    quirky_results = analyze_quirky_case_comprehensive(df)
    adjective_results = analyze_adjective_comprehensive(df)
    
    analyze_response_patterns_comprehensive(df)
    statistical_validation(df)
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE ANALYSIS COMPLETE")
    
    return {
        'middle_voice': middle_results,
        'umlaut': umlaut_results,
        'quirky_case': quirky_results,
        'adjective': adjective_results
    }

if __name__ == "__main__":
    results = main()