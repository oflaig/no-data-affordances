from collections.abc import MutableMapping
from copy import deepcopy
from typing import Tuple

from .utils import flatten

class Parameter():
    def __init__(self,
                 display_name: str,
                 default_val: float,
                 phase: str, 
                 output_transform = lambda x: x,
                 persist: bool = False):
        self.display_name = display_name
        self.default_val = default_val
        self.phase = phase
        self.output_transform = output_transform
        self.persist = persist

        self.value = self.default_val

    def get(self):
        return self.output_transform(self.value)

class DoubleParameter(Parameter):
    def __init__(self, 
                 input_range: Tuple, 
                 control_range = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.input_range = input_range
        
        if not control_range: # this could be unsafe if we accidentally read input range in the wrong place
            self.control_range = self.input_range
        else:
            self.control_range = control_range

class IntParameter(DoubleParameter):
    def get(self):
        return int(self.value)

class BoolParameter(DoubleParameter):
    def __init__(self, **kwargs):
        super().__init__(input_range=(0,1), **kwargs)

# Adapted from source - https://stackoverflow.com/a/21368848
# Posted by Aaron Hall, modified by community. See post 'Timeline' for change history
# Retrieved 2026-06-15, License - CC BY-SA 4.0
class ParameterTree(MutableMapping):
    def __init__(self, *args, **kwargs):
        '''Use the object dict'''
        self.__dict__.update(*args, **kwargs)
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def __getitem__(self, key):
        return self.__dict__[key]
    def __delitem__(self, key):
        del self.__dict__[key]
    def __iter__(self):
        return iter(self.__dict__)
    def __len__(self):
        return len(self.__dict__)
    def __str__(self):
        '''returns simple dict representation of the mapping'''
        return str(self.__dict__)
    def __repr__(self):
        '''echoes class, id, & reproducible representation in the REPL'''
        return '{}, ParameterTree({})'.format(super(ParameterTree, self).__repr__(), 
                                  self.__dict__)
    
    def update_tree(self, new_tree):
        """Update tree with dict of new values of the form:
                tree[scope][param] = value 
        where 'scope' is the model/param set being targeted (e.g. Generator 1, Global)."""
        new_tree = flatten(new_tree)

        for (scope, param), value in new_tree.items():
            self.__dict__[scope][param].value = value
    
    def copy(self):
        return deepcopy(self)
    
    def reset(self):
        for (scope, param) in flatten(self.__dict__).keys():
            if not self.__dict__[scope][param].persist:
                self.__dict__[scope][param].value = self.__dict__[scope][param].default_val

MODEL_TREES = {"Audio": {"Harmonic": {"num_harmonics": IntParameter(display_name="Number of harmonics", input_range=(6, 100), default_val=10, phase="setup"),
                                      "lr": DoubleParameter(display_name="Learning rate", input_range=(-2,2), control_range=(-2,2), default_val=0, phase="live_setup"),
                                      "momentum": DoubleParameter(display_name="Momentum", input_range=(-1,1), default_val=0, phase="live_setup"),
                                      "regularisation": DoubleParameter(display_name="Regularisation", input_range=(-1,1), default_val=0, phase="live_setup"),
                                      "quantisation": DoubleParameter(display_name="Quantisation", input_range=(0, 0.04), default_val=0, phase="live_setup"),
                                      "freq_skew": DoubleParameter(display_name="Frequency skew", input_range=(0, 1), default_val=0.4, output_transform=lambda x: ((1-x) * 2.5 + 0.5), phase="live_setup")},
                         "Harmonic drone": {"num_harmonics": IntParameter(display_name="Number of harmonics", input_range=(0, 100), default_val=10, phase="setup"),
                                            "pitch": DoubleParameter(display_name="Set pitch", input_range=(40, 5000), default_val=440, phase="setup"),
                                            "lr": DoubleParameter(display_name="Learning rate", input_range=(0,2), control_range=(0,0.5), default_val=0, phase="live_setup")},
                         "Additive": {"num_oscs": IntParameter(display_name="Number of oscillators", input_range=(0, 100), default_val=5, phase="setup"),
                                            "freq_skew": DoubleParameter(display_name="Frequency skew", input_range=(0, 1), default_val=0.4, output_transform=lambda x: ((1-x) * 2.5 + 0.5), phase="live_setup"),
                                            "lr": DoubleParameter(display_name="Learning rate", input_range=(0,2), control_range=(0,0.5), default_val=0, phase="live_setup")}},
               "Visual": {"MLP": {"lr": DoubleParameter(display_name="Learning rate", input_range=(0, 0.02), default_val=0, phase="live_setup")},
                          "CNN": {"lr": DoubleParameter(display_name="Learning rate", input_range=(0, 3), default_val=0, phase="live_setup")}}}

GLOBAL_TREE = {"ddsp_frames": IntParameter(display_name="DDSP frames", input_range=(4, 100), default_val=5, phase="setup"),
               "time_factor": IntParameter(display_name="Time factor", input_range=(1, 32), default_val=2, phase="setup"), # shouldn't be in this phase!!!
                "temperature": DoubleParameter(display_name="Temperature", input_range=(0.001, 1), default_val=0, phase="live_setup"),
                "tuning": DoubleParameter(display_name="Tuning", input_range=(0, 11.9), default_val=0, phase="live_setup"),
                "num_epochs": IntParameter(display_name="Number of epochs", input_range=(1, 10000), default_val=100, phase="test_settings"), #this range is arbritray and maybe unhelpful
                "sample_rate": IntParameter(display_name="Sample rate", input_range=(16000, 48000), default_val=16000, phase="test_settings"),
                "seeds_per_run": IntParameter(display_name="Seeds/run", input_range=(1, 20), default_val=1, phase="test_settings"),
                "render_video": BoolParameter(display_name="Render video", default_val=False, phase="test_settings"),
                "volume": DoubleParameter(display_name="Volume", input_range=(0, 1), default_val=1, phase="live")}
