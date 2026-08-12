import pandas as pd
import json
import numpy as np

def load_and_stratify(json_path: str, target_per_benchmark: int = 400, seed: int = 42) -> pd.DataFrame:
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    stratify_keys = {
        "ETHICS": "subset",
        "MMLU-Ethics": "subset",
        "TruthfulQA": "category",
        "Scruples": "label"
    }
    
    mm_mask = df['benchmark'] == 'Moral Machine'
    df.loc[mm_mask, 'mm_scenario'] = df[mm_mask]['question'].str.extract(
        r"(car must swerve|brakes failed|autonomous vehicle must choose)"
    )[0]
    stratify_keys["Moral Machine"] = "mm_scenario"

    sampled_dfs = []
    
    for benchmark, group in df.groupby('benchmark'):
        n_available = len(group)
        n_target = min(target_per_benchmark, n_available)
        
        strat_col = stratify_keys.get(benchmark)
        
        if strat_col and strat_col in group.columns and group[strat_col].notna().any():
            group[strat_col] = group[strat_col].fillna('Unknown')
            
            proportions = group[strat_col].value_counts(normalize=True)
            sampled = group.groupby(strat_col, group_keys=False).apply(
                lambda x: x.sample(n=int(np.round(proportions[x.name] * n_target)), random_state=seed),
                include_groups=False
            )
            
            if len(sampled) < n_target:
                shortfall = n_target - len(sampled)
                remaining = group.drop(sampled.index)
                sampled = pd.concat([sampled, remaining.sample(n=shortfall, random_state=seed)])
            elif len(sampled) > n_target:
                sampled = sampled.sample(n=n_target, random_state=seed)
                
            sampled_dfs.append(sampled)
        else:
            sampled_dfs.append(group.sample(n=n_target, random_state=seed))
            
    return pd.concat(sampled_dfs, ignore_index=True)

def main():
    input_file = "data/processed/all_benchmarks_unified.json"
    output_file = "data/processed/stratified_sample.json"
    
    print(f"Processing {input_file}...")
    stratified_df = load_and_stratify(input_file, target_per_benchmark=444)
    stratified_df.to_json(output_file, orient="records", indent=2)
    print(f"Sampled {len(stratified_df)} questions. Saved to {output_file}.")

if __name__ == "__main__":
    main()