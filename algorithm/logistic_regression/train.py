import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

try:
    from algorithm.logistic_regression.dataset import LABELS, load_data_splits
    from algorithm.logistic_regression.model import build_logistic_pipeline
except ImportError:
    try:
        from .dataset import LABELS, load_data_splits
        from .model import build_logistic_pipeline
    except ImportError:
        from dataset import LABELS, load_data_splits
        from model import build_logistic_pipeline


OUTPUT_DIR = Path(__file__).resolve().parent / "result"
DEFAULT_MODEL_PATH = OUTPUT_DIR / "tfidf_logistic_regression_model.joblib"

configs = [
    {
        "max_features": 5000,
        "ngram_range": (1, 1),
        "C": 0.1,
        "class_weight": None,
    },
    {
        "max_features": 10000,
        "ngram_range": (1, 2),
        "C": 1.0,
        "class_weight": "balanced",
    },
    {
        "max_features": 30000,
        "ngram_range": (1, 2),
        "C": 1.0,
        "class_weight": "balanced",
    },
    {
        "max_features": 50000,
        "ngram_range": (1, 2),
        "C": 10.0,
        "class_weight": "balanced",
    },
]


def evaluate_split(model, x, y_true, labels):
    y_pred = model.predict(x)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=labels,
            target_names=labels,
            zero_division=0,
            output_dict=True,
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


def tune_and_train(data_dir=None, output_dir=None, model_path=None, random_state=42, min_df=2, penalty="l2", solver="saga", max_iter=1000):
    x_train, x_valid, x_test, y_train, y_valid, y_test, data_stats = load_data_splits(data_dir=data_dir)
    class_names = [label for label in LABELS if label in set(y_train + y_valid + y_test)]

    best_score = -1.0
    best_config = None
    tuning_results = []

    for idx, cfg in enumerate(configs, start=1):
        print(f"\n=== Round {idx}/{len(configs)}: {cfg} ===")
        pipeline = build_logistic_pipeline(
            num_classes=len(set(y_train)),
            max_features=cfg["max_features"],
            ngram_range=cfg["ngram_range"],
            min_df=min_df,
            C=cfg["C"],
            penalty=penalty,
            solver=solver,
            max_iter=max_iter,
            random_state=random_state,
            class_weight=cfg["class_weight"],
        )
        pipeline.fit(x_train, y_train)

        y_val_pred = pipeline.predict(x_valid)
        val_macro_f1 = f1_score(y_valid, y_val_pred, average="macro", zero_division=0)
        print(f"Validation macro F1: {val_macro_f1:.4f}")

        tuning_results.append({
            "config": {**cfg, "ngram_range": list(cfg["ngram_range"])},
            "validation_macro_f1": val_macro_f1,
        })

        if val_macro_f1 > best_score:
            best_score = val_macro_f1
            best_config = cfg
            best_metrics = {
                "validation_macro_f1": val_macro_f1,
            }

    if best_config is None:
        raise RuntimeError("No valid configuration found during tuning.")

    print(f"\nBest config selected: {best_config}")
    print(f"Best validation macro F1: {best_score:.4f}")

    x_train_full = x_train + x_valid
    y_train_full = y_train + y_valid
    final_pipeline = build_logistic_pipeline(
        num_classes=len(set(y_train_full)),
        max_features=best_config["max_features"],
        ngram_range=best_config["ngram_range"],
        min_df=min_df,
        C=best_config["C"],
        penalty=penalty,
        solver=solver,
        max_iter=max_iter,
        random_state=random_state,
        class_weight=best_config["class_weight"],
    )
    final_pipeline.fit(x_train_full, y_train_full)

    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = Path(model_path) if model_path else output_dir / DEFAULT_MODEL_PATH.name
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_pipeline, model_path)

    test_metrics = evaluate_split(final_pipeline, x_test, y_test, labels=class_names)

    metadata = {
        "model": "TF-IDF + Logistic Regression",
        "class_names": class_names,
        "data_stats": data_stats,
        "train_label_distribution": dict(Counter(y_train_full)),
        "test_label_distribution": dict(Counter(y_test)),
        "best_config": {**best_config, "ngram_range": list(best_config["ngram_range"])},
        "best_valid_metrics": best_metrics,
        "params": {
            "random_state": random_state,
            "min_df": min_df,
            "penalty": penalty,
            "solver": solver,
            "max_iter": max_iter,
        },
        "model_path": str(model_path),
    }

    with open(output_dir / "train_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    with open(output_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "tuning": tuning_results,
                "best_valid": best_metrics,
                "test": test_metrics,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    with open(output_dir / "confusion_matrix.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([""] + class_names)
        for label, row in zip(class_names, test_metrics["confusion_matrix"]):
            writer.writerow([label] + row)

    with open(output_dir / "tuning_results.json", "w", encoding="utf-8") as f:
        json.dump(tuning_results, f, ensure_ascii=False, indent=2)

    return {
        **data_stats,
        "model_path": str(model_path),
        "output_dir": str(output_dir),
        "best_config": {**best_config, "ngram_range": list(best_config["ngram_range"])},
        "best_valid_macro_f1": best_score,
        "test_metrics": test_metrics,
    }


def main():
    parser = argparse.ArgumentParser(description="Tune and train TF-IDF + Logistic Regression with fixed configs.")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Directory containing train.jsonl, valid.jsonl, test.jsonl. Default: data/data_for_sentiment_analysis",
    )
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--model-out", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    stats = tune_and_train(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        model_path=args.model_out,
        random_state=args.random_state,
    )

    print("Training completed.")
    print(f"Data dir: {stats['data_dir']}")
    print(f"Train file: {stats['train_path']}")
    print(f"Valid file: {stats['valid_path']}")
    print(f"Test file: {stats['test_path']}")
    print(f"Best config: {stats['best_config']}")
    print(f"Best validation macro F1: {stats['best_valid_macro_f1']:.4f}")
    print(f"Saved model: {stats['model_path']}")
    print("Test metrics:")
    print(f"  Accuracy: {stats['test_metrics']['accuracy']:.4f}")
    print(f"  Macro F1: {stats['test_metrics']['macro_f1']:.4f}")
    print(f"  Weighted F1: {stats['test_metrics']['weighted_f1']:.4f}")


if __name__ == "__main__":
    main()
