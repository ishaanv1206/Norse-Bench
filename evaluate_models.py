import os
import csv
import random
import time
from dataclasses import dataclass
from tqdm import tqdm
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

@dataclass
class MinimalPair:
    id: str
    phenomenon: str
    grammatical: str
    ungrammatical: str
    target: str
    error_type: str

@dataclass
class EvaluationResult:
    pair_id: str
    model: str
    phenomenon: str
    grammatical: str
    ungrammatical: str
    prompt: str
    response: str
    choice: str
    correct: bool
    order: str

class APIKeyManager:
    def __init__(self):
        self.keys = []
        i = 1
        while True:
            key = os.getenv(f'GROQ_API_KEY_{i}')
            if key:
                self.keys.append(key)
                i += 1
            else:
                break
        main_key = os.getenv('GROQ_API_KEY')
        if main_key and main_key not in self.keys:
            self.keys.insert(0, main_key)
        if not self.keys:
            raise ValueError("No GROQ API keys found")
        print(f"Loaded {len(self.keys)} API keys")
        self.current_key_index = 0
        self.client = Groq(api_key=self.keys[self.current_key_index])
    
    def rotate_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        self.client = Groq(api_key=self.keys[self.current_key_index])
        print(f"Rotated to API key {self.current_key_index + 1}")
    
    def call_api(self, model, prompt, max_retries=3, timeout=30):
        is_openai = model.startswith('openai/')
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                if is_openai:
                    # OpenAI models need multi-turn + streaming + high max_tokens
                    completion = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": "I will analyze the sentences."},
                            {"role": "user", "content": ""}
                        ],
                        temperature=1,
                        max_completion_tokens=8192,
                        top_p=1,
                        stream=True,
                        stop=None,
                        timeout=timeout
                    )
                    full_response = ""
                    for chunk in completion:
                        if time.time() - start_time > timeout:
                            print(f"Timeout ({timeout}s), rotating key...")
                            self.rotate_key()
                            break
                        full_response += chunk.choices[0].delta.content or ""
                    else:
                        return full_response.strip()
                    continue  # Retry with new key after timeout
                else:
                    # Llama models work with simple format
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_completion_tokens=100,
                        top_p=1.0,
                        timeout=timeout
                    )
                    return response.choices[0].message.content.strip()
            except Exception as e:
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    print(f"Rate limit hit, rotating key...")
                    self.rotate_key()
                    time.sleep(1)
                    continue
                elif "organization_restricted" in error_str or "organization has been restricted" in error_str:
                    print(f"Organization restricted, rotating key...")
                    self.rotate_key()
                    time.sleep(1)
                    continue
                else:
                    print(f"API error (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        raise
        raise Exception(f"Failed after {max_retries} attempts")

class ModelEvaluator:
    def __init__(self):
        self.api_manager = APIKeyManager()
        self.models = [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
    
    def load_minimal_pairs(self, filepath="minimal_pairs.csv"):
        pairs = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pairs.append(MinimalPair(
                    id=row['id'],
                    phenomenon=row['phenomenon'],
                    grammatical=row['grammatical'],
                    ungrammatical=row['ungrammatical'],
                    target=row['target'],
                    error_type=row['error_type']
                ))
        return pairs
    
    def create_prompt(self, pair, shuffle=True):
        if shuffle and random.random() < 0.5:
            prompt = f"""Which of the following Old Norse sentences is grammatically correct?

A: {pair.ungrammatical}
B: {pair.grammatical}

Answer with A or B only."""
            order = "B_gram"
        else:
            prompt = f"""Which of the following Old Norse sentences is grammatically correct?

A: {pair.grammatical}
B: {pair.ungrammatical}

Answer with A or B only."""
            order = "A_gram"
        return prompt, order
    
    def parse_response(self, response):
        response = response.strip().upper()
        if 'A' in response and 'B' not in response:
            return 'A'
        elif 'B' in response and 'A' not in response:
            return 'B'
        elif response.startswith('A'):
            return 'A'
        elif response.startswith('B'):
            return 'B'
        return 'A'
    
    def evaluate_pair(self, pair, model, shuffle=True):
        prompt, order = self.create_prompt(pair, shuffle)
        try:
            response = self.api_manager.call_api(model, prompt)
            choice = self.parse_response(response)
            correct = (choice == 'A') if order == "A_gram" else (choice == 'B')
            return EvaluationResult(
                pair_id=pair.id, model=model, phenomenon=pair.phenomenon,
                grammatical=pair.grammatical, ungrammatical=pair.ungrammatical,
                prompt=prompt, response=response, choice=choice,
                correct=correct, order=order
            )
        except Exception as e:
            print(f"Error evaluating {pair.id}: {e}")
            return EvaluationResult(
                pair_id=pair.id, model=model, phenomenon=pair.phenomenon,
                grammatical=pair.grammatical, ungrammatical=pair.ungrammatical,
                prompt=prompt, response=f"ERROR: {e}", choice='A',
                correct=False, order=order
            )
    
    def load_existing_results(self, model):
        """Load existing results for a model to resume from."""
        filename = f"evaluation_results_{model.replace('/', '_')}.csv"
        completed_ids = set()
        results = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    completed_ids.add(row['pair_id'])
                    results.append(EvaluationResult(
                        pair_id=row['pair_id'],
                        model=row['model'],
                        phenomenon=row['phenomenon'],
                        grammatical=row['grammatical'],
                        ungrammatical=row['ungrammatical'],
                        prompt=row['prompt'],
                        response=row['response'],
                        choice=row['choice'],
                        correct=row['correct'] == 'True',
                        order=row['order']
                    ))
        return completed_ids, results
    
    def append_result(self, result, model):
        """Append a single result to the CSV file."""
        filename = f"evaluation_results_{model.replace('/', '_')}.csv"
        file_exists = os.path.exists(filename)
        with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['pair_id', 'model', 'phenomenon', 'grammatical',
                               'ungrammatical', 'prompt', 'response', 'choice', 'correct', 'order'])
            writer.writerow([result.pair_id, result.model, result.phenomenon, result.grammatical,
                           result.ungrammatical, result.prompt, result.response, result.choice, 
                           result.correct, result.order])
    
    def save_results(self, results, model):
        filename = f"evaluation_results_{model.replace('/', '_')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['pair_id', 'model', 'phenomenon', 'grammatical',
                           'ungrammatical', 'prompt', 'response', 'choice', 'correct', 'order'])
            for r in results:
                writer.writerow([r.pair_id, r.model, r.phenomenon, r.grammatical,
                               r.ungrammatical, r.prompt, r.response, r.choice, r.correct, r.order])
        print(f"Saved: {filename}")
    
    def evaluate_model(self, model, pairs, shuffle=True):
        print(f"\n=== Evaluating {model} ===")
        
        # Load existing progress
        completed_ids, results = self.load_existing_results(model)
        if completed_ids:
            print(f"Resuming from {len(completed_ids)} completed pairs")
        
        # Filter out already completed pairs
        remaining_pairs = [p for p in pairs if p.id not in completed_ids]
        
        if not remaining_pairs:
            print(f"All {len(pairs)} pairs already completed!")
            acc = sum(r.correct for r in results) / len(results) if results else 0
            print(f"{model}: {acc:.3f} ({sum(r.correct for r in results)}/{len(results)})")
            return results
        
        print(f"Remaining: {len(remaining_pairs)} pairs")
        
        pbar = tqdm(remaining_pairs, desc=model.split('/')[-1], initial=len(completed_ids), total=len(pairs))
        for pair in pbar:
            result = self.evaluate_pair(pair, model, shuffle)
            results.append(result)
            self.append_result(result, model)  # Save immediately
            acc = sum(r.correct for r in results) / len(results)
            pbar.set_postfix(acc=f"{acc:.3f}")
            time.sleep(0.1)
        
        acc = sum(r.correct for r in results) / len(results)
        print(f"{model}: {acc:.3f} ({sum(r.correct for r in results)}/{len(results)})")
        return results
    
    def compute_summary(self):
        all_dfs = []
        for model in self.models:
            filename = f"evaluation_results_{model.replace('/', '_')}.csv"
            if os.path.exists(filename):
                all_dfs.append(pd.read_csv(filename))
        if not all_dfs:
            print("No results found")
            return
        df = pd.concat(all_dfs, ignore_index=True)
        print("\n=== SUMMARY ===")
        print("\nOverall Accuracy:")
        for model in df['model'].unique():
            m_df = df[df['model'] == model]
            print(f"  {model}: {m_df['correct'].mean():.3f}")
        print("\nPer-phenomenon:")
        print(df.groupby(['model', 'phenomenon'])['correct'].mean().unstack().round(3))
        df.groupby(['model', 'phenomenon'])['correct'].mean().unstack().to_csv('evaluation_summary.csv', encoding='utf-8-sig')
        print("\nSaved: evaluation_summary.csv")
    
    def run(self):
        pairs = self.load_minimal_pairs()
        print(f"Loaded {len(pairs)} pairs")
        for model in self.models:
            self.evaluate_model(model, pairs)
        self.compute_summary()

if __name__ == "__main__":
    print("Old Norse LLM Evaluation")
    print("=" * 50)
    evaluator = ModelEvaluator()
    evaluator.run()
    print("\nDone!")
