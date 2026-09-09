import os
import glob
import re
import numpy as np
import librosa
from sklearn import metrics

def file_to_vectors(file_path, n_mels=128, n_fft=1024, hop_length=512, frames_concat=5):
    """
    Load a 10s audio file, extract log-mel spectrogram, and frame it into concatenated vectors.
    """
    # Load audio (keep native sample rate, which is 16000Hz)
    y, sr = librosa.load(file_path, sr=None)
    
    # Calculate spectrogram
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    mel = librosa.feature.melspectrogram(S=np.abs(stft)**2, sr=sr, n_mels=n_mels)
    log_mel = librosa.power_to_db(mel)
    
    # log_mel shape: (n_mels, n_frames) -> transpose to (n_frames, n_mels)
    log_mel = log_mel.T
    
    n_frames = log_mel.shape[0]
    vectors = []
    for i in range(n_frames - frames_concat + 1):
        vec = log_mel[i : i + frames_concat].flatten()
        vectors.append(vec)
        
    return np.array(vectors)

def list_files(target_dir, ext="wav"):
    """
    Recursively find all files in target_dir with extension ext.
    """
    search_path = os.path.join(target_dir, f"**/*.{ext}")
    return sorted(glob.glob(search_path, recursive=True))

def get_label_from_filename(filename):
    """
    Parse filename to extract anomaly label, section, and domain.
    Filename examples:
    - section_00_source_train_normal_0000_strength_1_ambient.wav
    - section_00_source_test_anomaly_0000.wav
    """
    basename = os.path.basename(filename)
    
    # Extract section
    section_match = re.search(r"section_(\d+)", basename)
    section = int(section_match.group(1)) if section_match else 0
    
    # Extract domain (source or target)
    domain = "target" if "target" in basename else "source"
    
    # Extract label (0 for normal, 1 for anomaly)
    label = 1 if "anomaly" in basename else 0
    
    return {
        "section": section,
        "domain": domain,
        "label": label,
        "basename": basename
    }

def calculate_metrics(y_true, y_pred, max_fpr=0.1):
    """
    Calculate AUC and pAUC for a set of true labels and anomaly scores.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # AUC
    auc = metrics.roc_auc_score(y_true, y_pred)
    
    # pAUC (partial AUC)
    p_auc = metrics.roc_auc_score(y_true, y_pred, max_fpr=max_fpr)
    
    return auc, p_auc
