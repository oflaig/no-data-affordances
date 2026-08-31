import numpy as np
import torch
import torch.nn as nn

import source.utils as u
from source.models import *
from source.audio import add_fades, radspersec_to_hertz, hertz_to_midi, MAJOR_SCALE

class Vanilla():
    codings_size = 30
    def __init__(self, params, sample_rate):
        self.SR = sample_rate
        self.n_frames = params["Global"]["ddsp_frames"].get()   

        self.coding = torch.normal(mean=0., std=1.0, size=(self.codings_size,))
        self.coding = self.coding.to(u.DEVICE)

        self.criterion = nn.BCELoss()

        self.generators = {}
        for name in ["Generator 1", "Generator 2"]:
            self.generators[name] = {}

            n_harmonics = params[name]["num_harmonics"].get()
            model = UnpitchedHarmonicGenerator(n_harmonics, 
                                                self.n_frames, 
                                                self.SR)

            feature_extractor = MelExtractor(sample_rate = self.SR,
                                                f_min = 20,
                                            n_mels=u.IMAGE_SHAPE[1], 
                                            n_fft=u.STFT_HOP * 4 * params["Global"]["time_factor"].get(), 
                                            hop_length=u.STFT_HOP * params["Global"]["time_factor"].get())  
            self.generators[name]["Feature extractor"] = feature_extractor

            gan_optimiser = torch.optim.SGD(model.parameters(), lr=0.03)
            quant_optimiser = torch.optim.Adam(model.parameters(), lr=0)
            self.generators[name]["Model"] = model.to(u.DEVICE)
            self.generators[name]["GAN optimiser"] = gan_optimiser
            self.generators[name]["Quant optimiser"] = quant_optimiser
        
        disc_model = GanDiscriminator
            
        disc_model = disc_model(image_height=28, 
                                image_width=28).to(u.DEVICE)
        disc_optimiser = torch.optim.SGD(disc_model.parameters(), lr=0)
        self.disc = {"Model": disc_model, "Optimiser": disc_optimiser}

    def run(self, params, model_data, n_samples):
        audio = np.zeros(shape=(2, n_samples))
        disc_loss = 0

        for j, (gen, gen_params) in enumerate(zip(self.generators.values(), 
                                                  [params["Generator 1"], params["Generator 2"]])):
            gen["GAN optimiser"].param_groups[0]['momentum'] = gen_params["momentum"].get()
            gen["GAN optimiser"].param_groups[0]['weight_decay'] = gen_params["regularisation"].get()
            gen["GAN optimiser"].zero_grad()

            gen_out, f0 = gen["Model"](n_samples, gen_params["freq_skew"].get())
                
            gen_audio = gen_out.clone().squeeze().detach().numpy()
            audio[j] = add_fades(gen_audio)
            gen_out = gen["Feature extractor"](gen_out)
            
            gen["Output"] = gen_out.detach()

            label_val = float((j+1)%len(self.generators))
            label = torch.tensor([label_val])
            gan_loss = self.criterion(self.disc["Model"](gen_out), label)
            model_data[f"Generator {j+1}"]["Loss"] = gan_loss.item()

            gan_loss.backward(retain_graph=True)

            for p in gen["Model"].parameters():
                if p.grad is not None: # quant_loss only affects some params
                    p.grad *= gen_params["lr"].get()

            gen["GAN optimiser"].step()
            gen["Quant optimiser"].param_groups[0]['lr'] = (gen_params["quantisation"].get())
            gen["Quant optimiser"].zero_grad()

            f0_Hz = radspersec_to_hertz(f0[0], self.SR)
            pitch = hertz_to_midi(f0_Hz)

            scale = np.sort((MAJOR_SCALE + params["Global"]["tuning"].get()) % 12)
            scale_pitches = []
            [scale_pitches.extend(scale + (12 * i)) for i in range(11)]
            scale_pitches = torch.tensor(scale_pitches)

            quant_loss = torch.empty_like(pitch)

            for i, note in enumerate(pitch):
                scale_dist = torch.min(torch.abs(note - scale_pitches))
                quant_loss[i] = scale_dist

            quant_loss = torch.mean(quant_loss) 
            model_data[f"Generator {j+1}"]["Quant loss"] = quant_loss.item()
            quant_loss.backward()
            gen["Quant optimiser"].step()

            model_data[f"Generator {j+1}"]["Image"] = gen_out.clone().squeeze().detach().numpy()

            disc_in = gen["Output"]
            temp = params["Global"]["temperature"].get() * 0.5
            target = torch.full((1,), float(abs(j - temp)))
            disc_loss += self.criterion(self.disc["Model"](disc_in), target)
    
        disc_params = params["Discriminator"]
        self.disc["Optimiser"].param_groups[0]['lr'] = disc_params["lr"].get()
        self.disc["Optimiser"].zero_grad()

        disc_loss /= len(self.generators)
        disc_loss.backward() 
        torch.nn.utils.clip_grad_norm_(self.disc["Model"].parameters(), max_norm=0.1)
        self.disc["Optimiser"].step()

        model_data["Discriminator"]["Loss"] = disc_loss.item()
        return audio, model_data