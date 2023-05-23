import numpy as np


def jupyter_use_whole_width_fix():
    from IPython.display import HTML, display

    display(HTML("<style>.container { width:100% !important; }</style>"))


def smart_normalize_audio(wav: np.ndarray, compensate_offset: bool = True):
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
    # if requested subtract the median to properly compensate the DC offset
    if compensate_offset:
        wav -= np.median(wav)
    return wav


def trim_vectors_to_same_len(*args):
    """Trims arbitrary number of vectors to the same length
    (minimum of all vectors). Useful for audio.

    Returns:
        list[np.ndarray]: A list of vectors that are trimmed to same len.
    """
    L = min([len(x) for x in args])
    return [x[:L] for x in args]
