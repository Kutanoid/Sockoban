#!/usr/bin/env python3

from tkinter import mainloop
from src.tk_gui import Program

if __name__ == '__main__':
    p = Program()
    p.settings.create_file_structure()
    mainloop()
