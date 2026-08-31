import torch
import torch.nn as nn
import numpy as np

MAJOR_SCALE = np.array([0, 2, 4, 7, 9])

def hertz_to_radspersec(freq, sample_rate):
    return 2*torch.pi*freq / sample_rate

def radspersec_to_hertz(freq, sample_rate):
    return (sample_rate*freq) / (2*torch.pi)

def hertz_to_midi(freq_Hz):
    return (12*torch.log2(freq_Hz/440)) + 69

def get_harmonic_frequencies(
        f0: torch.Tensor, #(B, n_frames)
        n_harmonics: int):
    harmonic_ratios = torch.arange(1, n_harmonics + 1).view(1, -1, 1)
    #Duplicate f0 for each harmonic
    f0 = f0.unsqueeze(1).repeat(1, n_harmonics, 1)
    return f0 * harmonic_ratios

def remove_above_nyquist(
        harmonic_amps: torch.Tensor,
        frequencies: torch.Tensor):
    """
    Zeroes out amplitude of fs above nyquist (in rad/sec)
    """
    return harmonic_amps * (frequencies < (torch.pi)).float() 

def add_fades(x):
    fade = np.linspace(0, 1, 100)

    if len(x) >= (2*len(fade)):
        x[:len(fade)] *= fade
        x[-len(fade):] *= fade[::-1]

    return x

def additive_synth(
        amplitude: torch.Tensor, #(B, n_sins, n_frames)
        angular_frequency: torch.Tensor, #(B, n_sins, n_frames)
        n_samples: int,
        phase_offset: torch.Tensor = None
        ) -> torch.Tensor:
    """
    Synthesises B frames of audio from frame-rate parameters by
    adding sinusoidal oscillators. 
    Adapted from https://intro2ddsp.github.io

    Args:
        amplitude: The amplitude of each oscillator at each frame, 
            from 0-1. 
        angular_frequency: Of each oscillator at each frame.
        n_samples: Of the target audio.
        phase_offset: Offset for each oscillator. 
    """
    
    # Upsample from frame rate to sample rate
    amplitude = nn.functional.interpolate(
        amplitude, 
        size=n_samples, 
        mode='linear')

    angular_frequency = nn.functional.interpolate(
        angular_frequency, 
        size=n_samples, 
        mode='nearest-exact')
    
    if phase_offset is None:
        phase_offset = torch.zeros_like(angular_frequency[:, :, :1])

    # Add initial phase to angular frequencies
    angular_frequency = torch.cat(
        [phase_offset, angular_frequency], dim=-1)
    # Remove last frequency to maintain correct length
    angular_frequency = angular_frequency[..., :-1]

    phase = torch.cumsum(angular_frequency, dim=-1)
    y = amplitude * torch.sin(phase)
    y = torch.sum(y, dim=1) 

    final_phase = phase[:, :, -1:].detach()

    return y, final_phase
