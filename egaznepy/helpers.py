import subprocess

import numpy as np
import scipy.signal


def jupyter_use_whole_width_fix():
    from IPython.display import HTML, display

    display(HTML("<style>.container { width:100% !important; }</style>"))


def align_signals(x, x_ref):
    """
    Aligns two signals time-wise and sign-wise.
    """
    aligned = np.zeros_like(x)
    L = len(aligned)
    lags = scipy.signal.correlation_lags(len(x), len(x_ref), mode="same")
    xc = scipy.signal.correlate(x, x_ref, mode="same")
    pos = np.argmax(np.abs(xc))
    offset = lags[pos]
    sign = np.sign(xc[pos])
    aligned[max(0, -offset) : min(L, L - offset)] = (
        sign * x[max(0, offset) : min(L, L + offset)]
    )
    return aligned


def smart_normalize_audio(
    wav: np.ndarray,
    compensate_offset: bool = True,
    dtype=np.float32,
):
    """
    .wav files have different specifications - sometimes data is stored as
    (signed) integers whereas in other times data is stored as (signed) floats.
    This code standardizes loaded .wav to have floating rate specifications
    without damaging the sound level in process.
    """
    try:
        np.finfo(wav.dtype)  # data is already float, return unmodified
    except:  # data is int, return adapted
        try:
            np.finfo(dtype)
        except TypeError:
            raise Exception(
                f"This function supports float dtypes only, {dtype} was supplied."
            )
        wav = wav.astype(dtype) / np.iinfo(wav.dtype).max
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


def invoke_command(*args):
    """
    Performs call to shell, captures (stdout, stderr) and returns it as a decoded string.
    Ensures that nothing is printed to the console.
    """
    out = subprocess.run(*args, capture_output=True, check=False, shell=True)
    return out.stdout.decode() + "\n" + out.stderr.decode()
