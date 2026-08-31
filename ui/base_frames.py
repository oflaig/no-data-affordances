from copy import deepcopy
import tkinter as tk
from tkinter import ttk

from .utils import *
from .params import *
from source.models import GENERATORS, DISCRIMINATORS

class ParamRow(ttk.Frame):
    def __init__(self, 
                 parent, 
                 label_text, 
                 widget_factory, 
                 default_val):
        super().__init__(parent)

        self.columnconfigure(1, weight=1)

        self.label = tk.Label(self, text=label_text)
        self.label.grid(row=0, column=0, sticky='w') 

        self.var = tk.DoubleVar(value=default_val)
        self.widget = widget_factory(self, self.var)
        self.widget.grid(row=0, column=1, sticky='ew')

    @property
    def value(self):
        return self.var.get()

def get_vcmd(parent, display_name, input_range):
    def vcmd(P):
        try:
            valid = (input_range[0] <= float(P) <= input_range[1])

        except:
            valid = False

        if not valid:
            input_alert(f"{display_name} should be a number between {input_range[0]} and {input_range[1]}")
        
        return valid
    return (parent.register(vcmd), '%P')

def get_invcmd(parent):
    def invcmd(W):
        parent.after_idle(lambda: parent.nametowidget(W).focus_set())
    return (parent.register(invcmd), '%W')

class ParamsEntryFrame(ttk.Frame):
    def __init__(self, parent, params):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)

        self.rows = {}

        for name, param in params.items():
            if type(param) == BoolParameter:
                widget_factory = lambda p, v: ttk.Checkbutton(p, variable=v)
            else:
                vcmd_factory = get_vcmd(self, param.display_name, param.input_range)
                widget_factory = lambda p, v: ttk.Entry(p, 
                                                    width=4, 
                                                    textvariable=v, 
                                                    validate='focusout', 
                                                    validatecommand=vcmd_factory, 
                                                    invalidcommand=get_invcmd(self))

            self.rows[name] = ParamRow(self, 
                                       label_text=param.display_name, 
                                       widget_factory=widget_factory, 
                                       default_val=param.default_val)
                                       
        for i, row in enumerate(self.rows.values()):
            row.grid(row=i, column=0, sticky=('e', 'w'))

    def get_values(self):
        return {name: row.value for name, row in self.rows.items()}

def get_slider_factory(param, app):
    def slider_factory(parent, var):
        row = ttk.Frame(parent)
        label = ttk.Label(row, 
                          text=f"{float(param.value):.2f}", 
                          width=4)        

        def slider_callback(a): 
            var.set(a)
            label['text'] = f"{float(a):.2f}"
            app.read_user_input()

        slider = ttk.Scale(row, 
                           value=param.value,
                           from_=param.control_range[0], 
                           to=param.control_range[1],
                           command=slider_callback)
        
        slider.grid(row=0, column=0, sticky='ew')
        label.grid(row=0, column=1, sticky='e')
        row.columnconfigure(0, weight=1)
        return row
    return slider_factory

    
class ParamsSliderFrame(ttk.Frame):
    def __init__(self, parent, params, app):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.app = app

        self.rows = {}

        for name, param in params.items():
            self.rows[name] = ParamRow(self, 
                            label_text=param.display_name, 
                            widget_factory=get_slider_factory(param, self.app), 
                            default_val=param.default_val)
            
        for i, row in enumerate(self.rows.values()):
            row.grid(row=i, column=0, sticky=('e', 'w'))

    def get_values(self):
        return {name: row.value for name, row in self.rows.items()}

class ModelPicker(ttk.Frame):
    """
    Contains labelled tree for selecting a model type.

    Attributes:
        options: Models available
        label: Text for label
        tree: ttk.Treeview for selection
        choice: Last model selected
    """
    def __init__(self, parent, options):
        """
        Args:
            options: List of models available, or nested dict 
                with additional categories like 'audio' or 
                'visual'
        """
        super().__init__(parent)

        self.parent = parent
        self.options = options

        self.tree = ttk.Treeview(self, show='tree', selectmode='browse', height=5)
        self.tree.grid(row=1, column=0, sticky=('n', 'e', 's', 'w'))

        self._fill_tree(options)

        self.choice = ()
        self.tree.bind("<<TreeviewSelect>>", self._tree_select)
    
    def _fill_tree(self, options, parent_node=''):
        """
        Recursively adds items from list or nested dict 
        into ttk.Treeview
        """
        is_leaf = not isinstance(options, dict)
        
        for node in options:
            self.tree.insert(parent_node, 'end', node, text=node)

            if not is_leaf:
                self._fill_tree(options[node], parent_node=node)
    
    def _tree_select(self, a):
        """
        If valid model selected (i.e. leaf rather than
        branch of the tree), updates list of parameters
        in parent ModelFrame if needed.
        """
        selected_item = self.tree.selection()[0]

        if self.tree.get_children(selected_item):
            return

        current_path = self._current_path
        
        if self.choice == current_path:
            return
        
        self.choice = current_path
        self.parent.update_param_list()

    @property
    def _current_path(self):
        """Current selection as tuple of levels"""
        selection = self.tree.selection()

        item = selection[0]
        nodes = []

        while item:
            nodes.append(self.tree.item(item, 'text'))
            item = self.tree.parent(item)

        return tuple(reversed(nodes))
    
class ModelFrame(ttk.LabelFrame):
    """Base class for generator or discriminator frame which 
    holds a ModelPicker and list of params.
    """
    def __init__(self, parent, phase, discriminator=False, **kwargs):
        super().__init__(parent, **kwargs)

        options = DISCRIMINATORS if discriminator else GENERATORS       
        self.discriminator = discriminator   

        self.phase = phase

        self.model_tree_label = tk.Label(self, text='Models')
        self.model_tree_label.grid(row=0, column=0, sticky='w')

        self.model_tree = ModelPicker(self, options)
        self.model_tree.grid(row=1, column=0, sticky=('n', 'e', 's', 'w'))

        self.model_params = None
        self.param_tree = None

    def update_param_list(self):
        setup_params = deepcopy(MODEL_TREES)
        if self.discriminator: setup_params = setup_params["Visual"]
        
        for key in self.model_tree.choice:
            setup_params = setup_params[key]
        
        if self.model_params and self.model_params.winfo_exists():
            self.model_params.destroy()
        
        self.param_tree = setup_params
        self.model_params = ParamsEntryFrame(self, {k: v for (k, v) in self.param_tree.items() if v.phase in self.phase})
        self.model_params.grid(row=2, column=0, sticky=('w', 'e'))

    def get_values(self):
        if not self.model_tree.choice:
            raise RuntimeError("No model chosen")
        
        params = {}

        if self.model_params: 
            params = self.model_params.get_values()

        for param, value in params.items():
            self.param_tree[param].value = value

        model_data = {'model_type': self.model_tree.choice}

        return self.param_tree, model_data