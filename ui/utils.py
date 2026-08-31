from tkinter import messagebox

def input_alert(message):
    messagebox.showinfo(title="Input error", message=message, icon='warning')

def flatten(dictionary, parent_key=[]):
    """
    Format nested dictionary as single-layer dictionary with
    tuples as keys
    """
    items = []

    for key, value in dictionary.items():
        new_key = parent_key + [key] if parent_key else [key]

        if isinstance(value, dict):
            items.extend(flatten(value, new_key).items())
        else:
            items.append((tuple(new_key), value))

    return dict(items)
