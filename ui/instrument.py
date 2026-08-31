import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from .base_frames import ParamsSliderFrame

class InstrumentFrame(ttk.Frame):
    CANVAS_W, CANVAS_H = (300, 300)

    def __init__(self, parent, app, model_data, param_tree):
        super().__init__(parent)

        self.app = app

        self.columnconfigure((0,1), weight=1)

        self.param_tree = param_tree
        self.model_data = model_data
        self.param_frames = {}
        self.image_frames = {}
        self.loss_vals = {}

        for i, name in enumerate(["Generator 1", "Generator 2", "Discriminator"]):
            model_params = self.param_tree[name]
            label_frame = ttk.LabelFrame(self, text=f"{name}: {self.model_data[name]["model_type"][-1]}")
            label_frame.grid(row=(i//2), column=(-i)%3, sticky=('ew'), columnspan=2)

            self.loss_vals[name] = tk.Variable()
            loss_row = ttk.Frame(label_frame)
            loss_row.grid(row=1, column=0)
            loss_row.columnconfigure(1, weight=1)
            loss_label = ttk.Label(loss_row, text="Loss")
            loss_label.grid(row=0, column=0)
            loss_display = ttk.Label(loss_row, textvariable=self.loss_vals[name])
            loss_display.grid(row=0, column=2)

            live_params = {k: v for (k, v) in model_params.items() if v.phase in ["live_setup", "live"]}
            
            self.param_frames[name] = ParamsSliderFrame(label_frame, live_params, app=self.app)
            self.param_frames[name].grid(row=2, sticky='ew')

            if name != "Discriminator":                 
                canvas = tk.Canvas(label_frame, width=self.CANVAS_W, height=self.CANVAS_H)
                canvas.grid(row=0)

                img_id = canvas.create_image(0, 0, anchor="nw")

                self.image_frames[name] = {"Canvas": canvas,
                                           "Image ID": img_id}
        
        buffer_frame = ttk.Frame(self, height=20)
        buffer_frame.grid(row=2)

        global_params = {k: v for (k, v) in self.param_tree["Global"].items() if v.phase in ["live_setup", "live"]}
        self.param_frames["Global"] = ParamsSliderFrame(self, global_params, app=self.app)
        self.param_frames["Global"].grid(row=3, column=1, columnspan=2, sticky=('ew'))

        panic_button = ttk.Button(self, text="Restart", command=self.master.reset_stream)
        panic_button.grid(row=4, column=0, sticky='w')
    
    def get_params(self):
        param_dict = {name: frame.get_values() for (name, frame) in self.param_frames.items()}
        return param_dict
    
    def update_data(self, model_data):
        for model in ["Generator 1", "Generator 2", "Discriminator"]:
            if "Loss" in model_data[model]:
                self.loss_vals[model].set(f"{float(model_data[model]["Loss"]):.2f}")

            if model != "Discriminator" and "Image" in model_data[model]:
                img = model_data[model]["Image"]
                img = Image.fromarray((img*255).astype(np.uint8), mode='L')
                img = img.resize((self.CANVAS_W, self.CANVAS_H), 
                                resample=Image.Resampling.BOX)
                self.image_frames[model]["Image"] = ImageTk.PhotoImage(img)
                canvas = self.image_frames[model]["Canvas"]
                canvas.itemconfig(self.image_frames[model]["Image ID"], 
                                image=self.image_frames[model]["Image"])
                
            