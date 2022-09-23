import uuid
from tkinter import ttk


def event_create():
    event_id = uuid.uuid4()
    return '<<' + str(event_id) + '>>'


ttk_style = ttk.Style()
