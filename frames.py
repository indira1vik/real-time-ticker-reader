import numpy as np

def frames_to_int(frames):
    if frames is None:
        return None
    return (frames * 255).astype(np.uint8)

def frames_to_float(frames):
    if frames is None:
        return None
    return (frames / 255).astype(np.float32)

def frames_gray(frames):
    if frames is None:
        return None
    return frames.mean(axis=2)

def frames_threshold(frames, minv = 0.0, maxv = 1.0):
    if frames is None:
        return None
    return np.maximum(np.minimum(frames, maxv), minv)
