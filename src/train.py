import os
import argparse
import json
import numpy as np
import tensorflow as tf
from common import list_files, file_to_vectors, get_label_from_filename, calculate_metrics
from model import get_model

def train_machine(machine_name, epochs=10, batch_size=512, step_size=5, quick_test=False):
    print(f"\n==========================================")
    print(f"Starting Training for Machine: {machine_name.upper()}")
    print(f"==========================================\n")
    
    # Base paths
    dataset_dir = os.path.join("dataset", f"dev_data_{machine_name}", machine_name)
    train_dir = os.path.join(dataset_dir, "train")
    source_test_dir = os.path.join(dataset_dir, "source_test")
    target_test_dir = os.path.join(dataset_dir, "target_test")
    
    # Check directory existence
    if not os.path.exists(train_dir):
        raise FileNotFoundError(f"Training directory not found: {train_dir}")
        
    os.makedirs("models", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # 1. Load Training Files
    train_files = list_files(train_dir)
    print(f"Found {len(train_files)} training files.")
    
    if quick_test:
        train_files = train_files[:10]
        epochs = 2
        print(f"[QUICK TEST] Downsampling to {len(train_files)} files, epochs={epochs}")
        
    # 2. Extract Features
    print("Extracting features from training files...")
    x_train_list = []
    file_sections = []
    
    for idx, f in enumerate(train_files):
        meta = get_label_from_filename(f)
        section = meta["section"]
        
        # Extract framed vectors
        vectors = file_to_vectors(f)
        # Downsample frames to speed up training on CPU
        vectors = vectors[::step_size]
        
        x_train_list.append(vectors)
        # Store section for each vector in this file
        file_sections.extend([section] * len(vectors))
        
        if (idx + 1) % 200 == 0 or (idx + 1) == len(train_files):
            print(f"Processed {idx + 1}/{len(train_files)} files...")
            
    x_train = np.concatenate(x_train_list, axis=0)
    file_sections = np.array(file_sections)
    print(f"Total training vectors: {x_train.shape}")
    
    # 3. Fit Autoencoder
    model = get_model(input_dim=x_train.shape[1])
    print(f"Training Autoencoder for {epochs} epochs...")
    model.fit(
        x_train, 
        x_train, 
        epochs=epochs, 
        batch_size=batch_size, 
        shuffle=True, 
        verbose=1
    )
    
    # Save the model
    model_path = os.path.join("models", f"{machine_name}_model.keras")
    model.save(model_path)
    print(f"Saved model to {model_path}")
    
    # 4. Calculate Thresholds (reconstruction error per section)
    # We calculate the reconstruction error for each file's vectors in training,
    # and compute the 90th percentile of clip-level anomaly scores.
    print("Calculating anomaly detection thresholds per section...")
    section_scores = {}
    
    for f in train_files:
        meta = get_label_from_filename(f)
        section = meta["section"]
        
        vectors = file_to_vectors(f)
        reconstructed = model(vectors, training=False).numpy()
        
        # Anomaly score of the clip is the mean squared error over all frames
        clip_error = np.mean(np.mean(np.square(vectors - reconstructed), axis=1))
        
        if section not in section_scores:
            section_scores[section] = []
        section_scores[section].append(float(clip_error))
        
    thresholds = {}
    for section, scores in section_scores.items():
        # Set threshold at 90th percentile (standard DCASE benchmark)
        thresholds[str(section)] = float(np.percentile(scores, 90))
        print(f"Section {section} Anomaly Threshold: {thresholds[str(section)]:.4f}")
        
    # Save thresholds and metadata
    meta_path = os.path.join("models", f"{machine_name}_meta.json")
    with open(meta_path, "w") as f_meta:
        json.dump({"thresholds": thresholds}, f_meta, indent=4)
    print(f"Saved metadata to {meta_path}")
    
    # 5. Evaluate on Test Sets
    print("Evaluating model performance on test sets...")
    test_results = {}
    
    for domain, test_dir in [("source", source_test_dir), ("target", target_test_dir)]:
        if not os.path.exists(test_dir):
            continue
            
        test_files = list_files(test_dir)
        print(f"Evaluating {domain} domain ({len(test_files)} files)...")
        
        # Group files by section
        section_files = {}
        for f in test_files:
            meta = get_label_from_filename(f)
            section = meta["section"]
            if section not in section_files:
                section_files[section] = []
            section_files[section].append(f)
            
        test_results[domain] = {}
        
        # Calculate AUC/pAUC per section
        for section, files in section_files.items():
            y_true = []
            y_pred = []
            
            for f in files:
                meta = get_label_from_filename(f)
                y_true.append(meta["label"])
                
                # Compute reconstruction error
                vectors = file_to_vectors(f)
                reconstructed = model(vectors, training=False).numpy()
                clip_error = np.mean(np.mean(np.square(vectors - reconstructed), axis=1))
                y_pred.append(float(clip_error))
                
            auc, p_auc = calculate_metrics(y_true, y_pred)
            test_results[domain][str(section)] = {
                "auc": float(auc),
                "pauc": float(p_auc)
            }
            print(f"  Section {section:02d} ({domain}): AUC = {auc:.4f}, pAUC = {p_auc:.4f}")
            
    # Save validation results
    metrics_path = os.path.join("results", f"{machine_name}_metrics.json")
    with open(metrics_path, "w") as f_metrics:
        json.dump(test_results, f_metrics, indent=4)
    print(f"Saved evaluation metrics to {metrics_path}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Autoencoder for DCASE 2021 Task 2 Machine")
    parser.add_argument("--machine", type=str, required=True, choices=["fan", "gearbox", "pump", "valve"], help="Machine type")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs to train")
    parser.add_argument("--batch_size", type=int, default=512, help="Batch size")
    parser.add_argument("--step_size", type=int, default=5, help="Step size for training vectors downsampling")
    parser.add_argument("--quick_test", action="store_true", help="Run a quick test training on a small subset")
    
    args = parser.parse_args()
    
    train_machine(
        machine_name=args.machine,
        epochs=args.epochs,
        batch_size=args.batch_size,
        step_size=args.step_size,
        quick_test=args.quick_test
    )
