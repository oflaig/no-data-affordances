import torch

DEVICE = 'cpu'
SR_CHOICES = [16000, 22050, 32000, 44100, 48000]
STFT_HOP = 64 
IMAGE_SHAPE = (28, 28) 

def scale_function(
        x: torch.Tensor,
        exponent: float = 2.3,
        max_value: float = 2.0,
        threshold: float = 1e-7):
    """
    Scales a parameter to a range of [threshold, max_value] with a slope of exponent.
    A threshold is used to stabilize the gradient near zero.
    Adapted from https://intro2ddsp.github.io
    """
    return (max_value * (torch.sigmoid(x) ** exponent)) + threshold