import numpy as np


def jupyter_use_whole_width_fix():
    from IPython.display import HTML, display

    display(HTML("<style>.container { width:100% !important; }</style>"))


def smart_normalize_audio(wav: np.ndarray):
    """
    .wav files have different specifications - sometimes data is stored as
    (signed) integers whereas in other times data is stored as (signed) floats.
    This code standardizes loaded .wav to have floating rate specifications
    without damaging the sound level in process.
    """
    try:
        np.finfo(wav.dtype)  # data is already float, return unmodified
    except:  # data is int, return adapted
        wav = wav.astype(np.float) / np.iinfo(wav.dtype).max
    return wav
