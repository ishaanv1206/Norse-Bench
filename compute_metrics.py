"""
Compute metrics and create visualizations for Old Norse LLM evaluation.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv

# Models evaluated
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

def load_all_results():
    """Load all evaluation result files."""
    all_dfs = []
    for model in MODELS:
        filename = f"evaluation_results_{model.replace('/', '_')}.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename, encoding='utf-8-sig')
            all_dfs.append(df)
            print(f"Loaded {len(df)} results from {filename}")
        else:
            print(f"Warning: {filename} not found")
    
    if not all_dfs:
        raise FileNotFoundError("No evaluation result files found")
    
    return pd.concat(all_dfs, ignore_index=True)

def compute_accuracy(df):
    """Compute overall accuracy per model."""
    accuracy = df.groupby('model')['correct'].mean()
    counts = df.groupby('model')['correct'].agg(['sum', 'count'])
    
    results = pd.DataFrame({
        'accuracy': accuracy,
        'correct': counts['sum'],
        'total': counts['count']
    })
    return results

def compute_phenomenon_accuracy(df):
    """Compute per-phenomenon accuracy for each model."""
    return df.groupby(['model', 'phenomenon'])['correct'].mean().unstack()

def compute_detailed_metrics(df):
    """Compute detailed metrics including counts per phenomenon."""
    metrics = {}
    
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        metrics[model] = {
            'overall_accuracy': model_df['correct'].mean(),
            'total_pairs': len(model_df),
            'correct_count': model_df['correct'].sum(),
            'per_phenomenon': {}
        }
        
        for phenomenon in model_df['phenomenon'].unique():
            phen_df = model_df[model_df['phenomenon'] == phenomenon]
            metrics[model]['per_phenomenon'][phenomenon] = {
                'accuracy': phen_df['correct'].mean(),
                'correct': phen_df['correct'].sum(),
                'total': len(phen_df)
            }
    
    return metrics

def plot_overall_accuracy(df, save_path='plot_overall_accuracy.png'):
    """Create bar chart comparing overall accuracy across models."""
    accuracy = df.groupby('model')['correct'].mean().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    colors = sns.color_palette("husl", len(accuracy))
    bars = plt.bar(range(len(accuracy)), accuracy.values, color=colors)
    
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.title('Overall Accuracy by Model\nOld Norse Grammaticality Judgment Task', fontsize=14)
    plt.xticks(range(len(accuracy)), [m.split('/')[-1] for m in accuracy.index], rotation=45, ha='right')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, accuracy.values)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")

def plot_phenomenon_heatmap(df, save_path='plot_phenomenon_heatmap.png'):
    """Create heatmap of model-phenomenon accuracy."""
    pivot = df.groupby(['model', 'phenomenon'])['correct'].mean().unstack()
    
    # Shorten model names for display
    pivot.index = [m.split('/')[-1] for m in pivot.index]
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdYlGn', 
                vmin=0, vmax=1, center=0.5,
                linewidths=0.5, cbar_kws={'label': 'Accuracy'})
    
    plt.title('Accuracy by Model and Phenomenon\nOld Norse Grammaticality Judgment Task', fontsize=14)
    plt.xlabel('Phenomenon', fontsize=12)
    plt.ylabel('Model', fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")



def save_metrics_csv(df, save_path='metrics.csv'):
    """Save detailed metrics to CSV."""
    metrics = compute_detailed_metrics(df)
    
    rows = []
    for model, data in metrics.items():
        # Overall row
        rows.append({
            'model': model,
            'phenomenon': 'OVERALL',
            'accuracy': data['overall_accuracy'],
            'correct': data['correct_count'],
            'total': data['total_pairs']
        })
        # Per-phenomenon rows
        for phen, phen_data in data['per_phenomenon'].items():
            rows.append({
                'model': model,
                'phenomenon': phen,
                'accuracy': phen_data['accuracy'],
                'correct': phen_data['correct'],
                'total': phen_data['total']
            })
    
    metrics_df = pd.DataFrame(rows)
    metrics_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"Saved: {save_path}")

def print_summary(df):
    """Print summary to console."""
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    
    print("\n--- Overall Accuracy ---")
    accuracy = compute_accuracy(df)
    for model in accuracy.index:
        acc = accuracy.loc[model, 'accuracy']
        correct = int(accuracy.loc[model, 'correct'])
        total = int(accuracy.loc[model, 'total'])
        print(f"  {model}: {acc:.3f} ({correct}/{total})")
    
    print("\n--- Per-Phenomenon Accuracy ---")
    phen_acc = compute_phenomenon_accuracy(df)
    print(phen_acc.round(3).to_string())
    
    print("\n--- Best/Worst Performance ---")
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        phen_acc = model_df.groupby('phenomenon')['correct'].mean()
        best = phen_acc.idxmax()
        worst = phen_acc.idxmin()
        print(f"  {model.split('/')[-1]}:")
        print(f"    Best:  {best} ({phen_acc[best]:.3f})")
        print(f"    Worst: {worst} ({phen_acc[worst]:.3f})")

def main():
    print("Computing metrics and generating visualizations...")
    print("=" * 60)
    
    # Load data
    df = load_all_results()
    print(f"\nTotal evaluations: {len(df)}")
    
    # Print summary
    print_summary(df)
    
    # Save metrics
    save_metrics_csv(df)
    
    # Generate plots
    print("\n--- Generating Visualizations ---")
    plot_overall_accuracy(df)
    plot_phenomenon_heatmap(df)
    
    # Save summary CSV
    compute_phenomenon_accuracy(df).to_csv('evaluation_summary.csv', encoding='utf-8-sig')
    print("Saved: evaluation_summary.csv")
    
    print("\n" + "=" * 60)
    print("Done!")

if __name__ == "__main__":
    main()
