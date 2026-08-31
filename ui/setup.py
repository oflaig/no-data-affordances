from copy import deepcopy
import tkinter as tk

from .base_frames import *
from .params import ParameterTree

class SetupFrame(tk.Frame):
    """
    Currently the run button callback to start training relies on this being 
    within some parent class which has a function called 'finish_setup'
    """
    def __init__(self, parent, mode):
        super().__init__(parent)

        if not mode in ['instrument', 'static']:
            raise ValueError(f"Setup mode {mode} not recognised")
        
        if mode == "instrument": 
            self.phase = ["setup"]
        elif mode == "static":
            self.phase = ["setup", "live_setup", "test_settings"]

        self.genL_frame = ModelFrame(self, text="Generators 1 and 2", phase=self.phase)
        self.genL_frame.grid(row=0, column=0, sticky='n')

        self.genR_frame = ModelFrame(self, text="Generator 2", phase=self.phase)
        
        self.gen_link = tk.BooleanVar(value=True)
        self.gen_link_choice = ttk.Checkbutton(self, 
                                        text='Duplicate', 
                                        variable=self.gen_link, 
                                        command=self.link_generators)
        self.gen_link_choice.grid(row=1, column=0, sticky='w')

        self.disc_frame = ModelFrame(self, discriminator=True, text = "Discriminator", phase=self.phase)
        self.disc_frame.grid(row=2, column=0, columnspan=1, sticky='w')

        self.run_frame = ttk.LabelFrame(self, text="Global")
        self.run_frame.grid(row=2, column=1, sticky=('n', 'e', 's'))
        self.run_frame.rowconfigure(1, weight=1)
        
        self.run_params = ParamsEntryFrame(self.run_frame, {k: v for (k, v) in deepcopy(GLOBAL_TREE).items() if v.phase in self.phase})
        self.run_params.grid(row=0, sticky=('e', 'n'))

        self.run_button = ttk.Button(self.run_frame, text="Run", command=self.master.finish_setup)
        self.run_button.grid(row=2, sticky=('e', 's'))
        
    def link_generators(self):
        if self.gen_link.get():
            self.genL_frame['text'] = 'Generators 1 and 2'
            self.genR_frame.grid_remove()
        else:
            self.genL_frame['text'] = 'Generator 1'
            self.genR_frame.grid(row=0, column=1, sticky='n')

    def get_params(self):
        params = {}
        model_data = {}

        for name, frame in {"Generator 1": self.genL_frame,
                            "Generator 2": self.genR_frame,
                            "Discriminator": self.disc_frame
                            }.items():
            
            if name == "Generator 2" and self.gen_link.get():
                params["Generator 2"] = deepcopy(params['Generator 1'])
                model_data[name] = deepcopy(model_data['Generator 1'])
                continue
            
            try:
                params[name], model_data[name] = frame.get_values()
            except:
                return
        
        global_tree = deepcopy(GLOBAL_TREE)

        for param, value in self.run_params.get_values().items():
            global_tree[param].value = value

        return ParameterTree(params | {"Global": global_tree}), model_data