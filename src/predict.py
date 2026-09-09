import os
import argparse
import json
import numpy as np
import tensorflow as tf
from common import file_to_vectors, get_label_from_filename

def predict_file(model_path, meta_path, file_path):
    # 1. Load metadata and thresholds
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Metadata file not found: {meta_path}")
    with open(meta_path, "r") as f_meta:
        meta_data = json.load(f_meta)
    thresholds = meta_data.get("thresholds", {})
    
    # 2. Parse file details
    file_info = get_label_from_filename(file_path)
    section = str(file_info["section"])
    domain = file_info["domain"]
    
    # Retrieve threshold for the file's section (default to 0.0 if not found)
    threshold = thresholds.get(section, 0.0)
    
    # 3. Load model
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    model = tf.keras.models.load_model(model_path)
    
    # 4. Extract features
    vectors = file_to_vectors(file_path)
    
    # 5. Run inference
    reconstructed = model(vectors, training=False).numpy()
    
    # Anomaly score is the average reconstruction error over all frames
    frame_errors = np.mean(np.square(vectors - reconstructed), axis=1)
    clip_score = float(np.mean(frame_errors))
    
    # Classify based on threshold
    is_anomaly = clip_score > threshold
    
    result = {
        "file": os.path.basename(file_path),
        "section": int(section),
        "domain": domain,
        "anomaly_score": clip_score,
        "threshold": threshold,
        "is_anomaly": bool(is_anomaly),
        "ground_truth": file_info["label"],
        "frame_scores": frame_errors.tolist() # useful for plotting
    }
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict anomaly for a single machine sound clip")
    parser.add_argument("--model", type=str, required=True, help="Path to trained keras model")
    parser.add_argument("--meta", type=str, required=True, help="Path to meta JSON file with thresholds")
    parser.add_argument("--file", type=str, required=True, help="Path to the WAV audio file")
    
    args = parser.parse_args()
    
    res = predict_file(args.model, args.meta, args.file)
    print(json.dumps({k: v for k, v in res.items() if k != 'frame_scores'}, indent=4))
