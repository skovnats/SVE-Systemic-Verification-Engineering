#!/usr/bin/env python3
"""
Learned TIK Predictor — Fine-tune RoBERTa-large for TIK score prediction.

Multi-task: 
  - Regression: predict 7 TIK components (MSE loss)
  - Classification: predict H/F flags (BCE loss)

Designed to run on Google Colab free tier (T4 GPU).

Usage:
  python learned_predictor.py --data data/processed/benchmarkmeta.json --output results/checkpoints/
"""

import os
import json
import argparse
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, RobertaModel, AdamW, get_linear_schedule_with_warmup


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class TIKDataset(Dataset):
    def __init__(self, questions: list, tokenizer, max_length: int = 256):
        self.questions = questions
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, idx):
        q = self.questions[idx]
        text = q["question"]
        
        encoding = self.tokenizer(
            text, max_length=self.max_length, padding="max_length",
            truncation=True, return_tensors="pt"
        )
        
        # 7 TIK components
        tik = q.get("tik_components", {})
        regression_targets = torch.tensor([
            tik.get("TIK_Q", 0.5), tik.get("TIK_E", 0.5),
            tik.get("TIK_I", 0.5), tik.get("TIK_S", 0.5),
            tik.get("TIK_O", 0.5), tik.get("TIK_T", 0.5),
            tik.get("TIK_M", 0.5),
        ], dtype=torch.float)
        
        # H/F binary flags
        classification_targets = torch.tensor([
            float(tik.get("ontological_hole", False)),
            float(tik.get("forbidden_fruit", False)),
        ], dtype=torch.float)
        
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "regression_targets": regression_targets,
            "classification_targets": classification_targets,
            "benchmark": q.get("benchmark", ""),
        }


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class TIKPredictor(nn.Module):
    """RoBERTa-large + multi-task head."""
    
    def __init__(self, model_name: str = "roberta-large",
                 regression_dim: int = 7, classification_dim: int = 2):
        super().__init__()
        self.roberta = RobertaModel.from_pretrained(model_name)
        hidden = self.roberta.config.hidden_size  # 1024 for large
        
        # Regression head: 7 TIK components
        self.regression_head = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, regression_dim),
            nn.Sigmoid(),  # TIK scores are in [0, 1]
        )
        
        # Classification head: H/F flags
        self.classification_head = nn.Sequential(
            nn.Linear(hidden, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, classification_dim),
            nn.Sigmoid(),
        )
    
    def forward(self, input_ids, attention_mask):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]  # [CLS] token
        
        regression = self.regression_head(cls_output)
        classification = self.classification_head(cls_output)
        
        return regression, classification


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_epoch(model, loader, optimizer, scheduler, device, reg_weight=1.0, cls_weight=0.5):
    model.train()
    total_loss = 0
    reg_criterion = nn.MSELoss()
    cls_criterion = nn.BCELoss()
    
    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        reg_targets = batch["regression_targets"].to(device)
        cls_targets = batch["classification_targets"].to(device)
        
        optimizer.zero_grad()
        reg_pred, cls_pred = model(input_ids, attention_mask)
        
        loss_reg = reg_criterion(reg_pred, reg_targets) * reg_weight
        loss_cls = cls_criterion(cls_pred, cls_targets) * cls_weight
        loss = loss_reg + loss_cls
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
    
    return total_loss / len(loader)


def evaluate(model, loader, device):
    model.eval()
    all_reg_preds, all_reg_targets = [], []
    all_cls_preds, all_cls_targets = [], []
    
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            
            reg_pred, cls_pred = model(input_ids, attention_mask)
            
            all_reg_preds.append(reg_pred.cpu().numpy())
            all_reg_targets.append(batch["regression_targets"].numpy())
            all_cls_preds.append(cls_pred.cpu().numpy())
            all_cls_targets.append(batch["classification_targets"].numpy())
    
    reg_preds = np.concatenate(all_reg_preds)
    reg_targets = np.concatenate(all_reg_targets)
    cls_preds = np.concatenate(all_cls_preds)
    cls_targets = np.concatenate(all_cls_targets)
    
    # MAE for regression
    mae = np.mean(np.abs(reg_preds - reg_targets))
    
    # AUC for classification
    from sklearn.metrics import roc_auc_score
    try:
        h_auc = roc_auc_score(cls_targets[:, 0], cls_preds[:, 0])
        f_auc = roc_auc_score(cls_targets[:, 1], cls_preds[:, 1])
    except ValueError:
        h_auc = f_auc = 0.5
    
    return {"mae": mae, "h_auc": h_auc, "f_auc": f_auc}


# ---------------------------------------------------------------------------
# Cross-benchmark evaluation (LOBO)
# ---------------------------------------------------------------------------

def leave_one_benchmark_out(questions, benchmarks):
    """Generator: yield (train, test, test_benchmark_name) for LOBO eval."""
    for bm in benchmarks:
        train = [q for q in questions if q.get("benchmark") != bm]
        test = [q for q in questions if q.get("benchmark") == bm]
        if test:
            yield train, test, bm


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to BenchmarkMeta JSON")
    parser.add_argument("--output", default="results/checkpoints/")
    parser.add_argument("--model", default="roberta-large")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--lobo", action="store_true", help="Run leave-one-benchmark-out")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    # Load data
    with open(args.data) as f:
        questions = json.load(f)
    
    print(f"Loaded {len(questions)} questions")
    
    # Tokenizer
    tokenizer = RobertaTokenizer.from_pretrained(args.model)
    
    # Standard train/val/test split
    from sklearn.model_selection import train_test_split
    benchmarks_list = [q.get("benchmark", "") for q in questions]
    
    train_q, test_q = train_test_split(
        questions, test_size=0.15, stratify=benchmarks_list, random_state=42)
    benchmarks_train = [q.get("benchmark", "") for q in train_q]
    train_q, val_q = train_test_split(
        train_q, test_size=0.176, stratify=benchmarks_train, random_state=42)  # 0.176 of 0.85 ≈ 0.15
    
    train_ds = TIKDataset(train_q, tokenizer)
    val_ds = TIKDataset(val_q, tokenizer)
    test_ds = TIKDataset(test_q, tokenizer)
    
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size)
    
    # Model
    device = torch.device(args.device)
    model = TIKPredictor(args.model).to(device)
    
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=total_steps // 10, num_training_steps=total_steps)
    
    # Training loop
    best_val_mae = float("inf")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(args.epochs):
        loss = train_epoch(model, train_loader, optimizer, scheduler, device)
        val_metrics = evaluate(model, val_loader, device)
        
        print(f"Epoch {epoch+1}/{args.epochs}: loss={loss:.4f}, "
              f"val_MAE={val_metrics['mae']:.4f}, "
              f"val_H_AUC={val_metrics['h_auc']:.4f}, "
              f"val_F_AUC={val_metrics['f_auc']:.4f}")
        
        if val_metrics["mae"] < best_val_mae:
            best_val_mae = val_metrics["mae"]
            torch.save(model.state_dict(), output_dir / "best_model.pt")
            print(f"  → Saved best model (MAE={best_val_mae:.4f})")
    
    # Final test evaluation
    model.load_state_dict(torch.load(output_dir / "best_model.pt"))
    test_metrics = evaluate(model, test_loader, device)
    print(f"\nTest results: MAE={test_metrics['mae']:.4f}, "
          f"H_AUC={test_metrics['h_auc']:.4f}, F_AUC={test_metrics['f_auc']:.4f}")
    
    # Save results
    with open(output_dir / "test_results.json", "w") as f:
        json.dump(test_metrics, f, indent=2)
    
    # LOBO evaluation
    if args.lobo:
        print("\n" + "="*60)
        print("Leave-One-Benchmark-Out Evaluation")
        print("="*60)
        
        benchmarks = list(set(q.get("benchmark", "") for q in questions))
        lobo_results = {}
        
        for train_q_lobo, test_q_lobo, bm_name in leave_one_benchmark_out(questions, benchmarks):
            print(f"\nHeld out: {bm_name} ({len(test_q_lobo)} questions)")
            
            # Retrain (simplified — in practice use full training loop)
            train_ds_lobo = TIKDataset(train_q_lobo, tokenizer)
            test_ds_lobo = TIKDataset(test_q_lobo, tokenizer)
            train_loader_lobo = DataLoader(train_ds_lobo, batch_size=args.batch_size, shuffle=True)
            test_loader_lobo = DataLoader(test_ds_lobo, batch_size=args.batch_size)
            
            model_lobo = TIKPredictor(args.model).to(device)
            opt_lobo = AdamW(model_lobo.parameters(), lr=args.lr, weight_decay=0.01)
            steps = len(train_loader_lobo) * 3  # Fewer epochs for LOBO
            sched_lobo = get_linear_schedule_with_warmup(opt_lobo, steps // 10, steps)
            
            for ep in range(3):
                train_epoch(model_lobo, train_loader_lobo, opt_lobo, sched_lobo, device)
            
            metrics = evaluate(model_lobo, test_loader_lobo, device)
            lobo_results[bm_name] = metrics
            print(f"  MAE={metrics['mae']:.4f}, H_AUC={metrics['h_auc']:.4f}")
        
        with open(output_dir / "lobo_results.json", "w") as f:
            json.dump(lobo_results, f, indent=2)


if __name__ == "__main__":
    main()
