import torch
from torch import nn
from torchaudio.transforms import MelSpectrogram

from .audio import hertz_to_radspersec, get_harmonic_frequencies, remove_above_nyquist, additive_synth
import source.utils as u

DISCRIMINATORS = ['MLP'] 
GENERATORS = {'Audio': ['Harmonic']}

class MelExtractor(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.melspectrogram = MelSpectrogram(**kwargs)

    def forward(self, x):
        x = self.melspectrogram(x)
        x = torch.log10(1 + 100 * x) # Log compression
        x = torch.flip(x, (1,))
        return x


class PitchedHarmonicGenerator(nn.Module):
    def __init__(self, 
                 n_harmonics: int,
                 n_frames: int,
                 sample_rate: int):
        super().__init__()
        
        self.sample_rate = sample_rate
        self.n_harmonics = n_harmonics
        self.n_frames = n_frames
        self.harmonic_amplitudes = nn.Parameter(
            torch.randn((1, n_harmonics, n_frames)))
        self.global_amp = nn.Parameter(torch.randn((1, n_frames)))
        self.register_buffer('phase_state', torch.zeros(1, n_harmonics, 1))

    def forward(self, ang_freq, n_samples):
        harmonic_freqs = get_harmonic_frequencies(ang_freq, self.n_harmonics) 

        harmonic_amps = u.scale_function(self.harmonic_amplitudes, max_value = 0.9)
        harmonic_amps = remove_above_nyquist(harmonic_amps, harmonic_freqs)
        # Normalise 
        harmonic_amps = harmonic_amps / torch.sum(harmonic_amps, dim=1, keepdim=True)

        global_amp = u.scale_function(self.global_amp, max_value=0.9, exponent=0.5)
        harmonic_amps *= global_amp.unsqueeze(1)

        x, final_phase = additive_synth(harmonic_amps, harmonic_freqs, n_samples, self.phase_state)
        self.phase_state = final_phase - ((final_phase // torch.pi) * torch.pi)
        return x, ang_freq
    
class UnpitchedHarmonicGenerator(PitchedHarmonicGenerator):
    def __init__(self, 
                 n_harmonics: int,
                 n_frames: int,
                 sample_rate: int):
        super().__init__(n_harmonics, n_frames, sample_rate)

        self.ang_freq = nn.Parameter(
            torch.randn((1, n_frames)))
        self.max_freq = hertz_to_radspersec(((sample_rate // 2) - 1e-3) / n_harmonics, sample_rate)
    
    def forward(self, n_samples, freq_skew):
        ang_freq = u.scale_function(self.ang_freq,
                                  threshold=0.04, 
                                  max_value=self.max_freq,
                                  exponent=freq_skew)
        return super().forward(ang_freq, n_samples)

class GanDiscriminator(nn.Module):
    def __init__(self,
                 image_height,
                 image_width):
        super().__init__()
        self.flatten = nn.Flatten()

        self.lin1 = nn.Linear(image_height*image_width, 150)
        self.lin2 = nn.Linear(150, 100)
        self.lin3 = nn.Linear(100, 1)
        self.selu = nn.SELU()
        self.sig  = nn.Sigmoid()

    def forward(self, x):
        x = torch.squeeze(x, 1)
        x = self.flatten(x)

        x = self.lin1(x)
        x = self.selu(x)
        x = self.lin2(x)
        x = self.selu(x)
        x = self.lin3(x)
        x = self.sig(x)
        x = x.squeeze(1)

        return x
    