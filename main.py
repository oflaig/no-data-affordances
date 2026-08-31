from copy import deepcopy
import sounddevice as sd
import tkinter as tk
from tkinter import ttk

from ui.setup import SetupFrame
from ui.instrument import InstrumentFrame
from ui.utils import *
from ui.params import *

import source.utils as u
from train import Vanilla

class AudioStream(sd.OutputStream):
    def __init__(self, app):
        self.app = app
        param_tree = deepcopy(self.app.param_tree)

        time_factor = param_tree["Global"]["time_factor"].get()
        self.n_samples = (u.IMAGE_SHAPE[1] - 1) * u.STFT_HOP * time_factor
        self.model = Vanilla(param_tree, sample_rate=sd.default.samplerate)

        super().__init__(blocksize=self.n_samples, 
                         channels=2, 
                         callback=self.callback)
        
    def callback(self, outdata, frames, time, status):
        param_tree = self.app.param_tree.copy()
        x, self.app.model_data = self.model.run(param_tree, self.app.model_data, self.n_samples)
        outdata[:] = x.T * param_tree["Global"]["volume"].get() * 0.6
        print(f"CPU load: {(self.cpu_load*100):.2f}%", end='\r')
    
    def reset(self):
        param_tree = deepcopy(self.app.param_tree)
        model_data = deepcopy(self.app.model_data)
        self.model = Vanilla(param_tree,
                        model_data,
                        sample_rate=sd.default.samplerate)
        
class ApplicationFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.parent.title('Setup')
        self.grid(row=0, column=0)

        self.param_tree = None
        self.model_data = None

        self.setup_frame = SetupFrame(self, mode="instrument")
        self.setup_frame.grid(row=0, column=0)

        self.run_window = None
        self.device_window = None

    def finish_setup(self):
        params = self.setup_frame.get_params()
        if not params: return 
        
        self.param_tree, self.model_data = params

        if self.run_window: 
            self.run_window.destroy()

        self.run_window = RunWindow(self)
        self.run_window.start_stream()
        
        self.lower()

    def open_settings(self):
        if not self.device_window or not self.device_window.winfo_exists():
            self.device_window = AudioSettingsWindow(self.master)
        
        self.device_window.lift()

    def read_user_input(self):
        self.param_tree.update_tree(self.run_window.instrument_frame.get_params())

class RunWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.title('Run')

        self.instrument_frame = InstrumentFrame(self, 
                                                app=parent,
                                                model_data=deepcopy(self.parent.model_data),
                                                param_tree=self.parent.param_tree.copy())
        self.instrument_frame.grid(row=0)

        self.audio_stream = None

    def start_stream(self):
        self.ui_update_stream()

        self.audio_stream = AudioStream(app=self.parent)
        self.audio_stream.start()

    def ui_update_stream(self):
        if self.audio_stream:
            model_data = deepcopy(self.parent.model_data)

            if model_data and ("Image" in model_data["Generator 1"]):
                self.instrument_frame.update_data(model_data)
        
        self.after(50, self.ui_update_stream)

    def reset_stream(self):
        if self.audio_stream:
            self.audio_stream.reset()

    def destroy(self):
        self.audio_stream.stop()
        super().destroy()

class AudioSettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title('Audio settings')
        self.columnconfigure(1, weight=1)

        device_label = tk.Label(self, text="Output device")
        device_label.grid(row=0, column=0, sticky='e')

        self.current_device = sd.query_devices(kind='output')['name']
        available_devices = []

        for device in sd.query_devices():
            if device['max_output_channels'] >= 2:
                available_devices.append(device['name'])

        self.device_selection = tk.StringVar(value=self.current_device)
        self.device_dropdown = ttk.Combobox(self, 
                                     state='readonly', 
                                     values=available_devices,
                                     textvariable=self.device_selection)
        self.device_dropdown.bind('<<ComboboxSelected>>', self.select_device)
        self.device_dropdown.grid(row=0, column=2, sticky='w')

        self.sr_label = tk.Label(self, text='Sample rate')
        self.sr_label.grid(row=1, column=0, sticky='e')

        self.sr_selection = tk.StringVar(value=sd.default.samplerate)
        self.sr_dropdown = ttk.Combobox(self, 
                                        state='readonly', 
                                        values=u.SR_CHOICES,
                                        textvariable=self.sr_selection)
        self.sr_dropdown.bind('<<ComboboxSelected>>', self.select_sr)
        self.sr_dropdown.grid(row=1, column=2, sticky='w')

    def select_device(self, a):
        self.device_dropdown.selection_clear()
        selection = self.device_selection.get()         
        
        if selection != self.current_device:
            sd.default.device = selection
            self.current_device = sd.query_devices(kind='output')['name']
            print(f"Changed audio device - now using {self.current_device}")
            print("This change will be applied upon initialising a new run")

    def select_sr(self, a):
        self.sr_dropdown.selection_clear()
        selection = self.sr_selection.get()

        if selection != sd.default.samplerate:
            sd.default.samplerate = int(selection)
            print(f"Changed sample rate - now using {sd.default.samplerate}")
            print("This change will be applied upon initialising a new run")

def main():
    sd.default.samplerate = 16000

    root = tk.Tk()
    app = ApplicationFrame(root)

    root.option_add('*tearOff', False) # Needed for menu formatting
    menu_bar = tk.Menu(root)
    root['menu'] = menu_bar

    audio_menu = tk.Menu(menu_bar)
    menu_bar.add_cascade(menu=audio_menu, label='Audio')

    audio_menu.add_command(label='Audio settings', command=app.open_settings)

    root.mainloop()

if __name__=="__main__":
    main()