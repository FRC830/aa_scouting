""" Debugging """

from __future__ import print_function

import code, readline

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

class Console:
    def __init__(self, globals=None):
        if globals is None:
            globals = {}
        self.globals = globals
        self.globals['quit'] = self.globals['exit'] = self.quit

    def add_to_menubar(self, menubar):
        menu = Menu(menubar)
        menubar.add_cascade(label='Debug', menu=menu)
        menu.add_command(label='Console', command=self.run_console)

    def run_console(self):
        self.console = code.InteractiveConsole(self.globals)
        try:
            self.console.interact('Console started.')
        except SystemExit as e:
            print('Console closed.')
            if len(e.args) and e.args[0]:
                # Make exit(1) exit program
                raise

    def quit(self, force=False):
        """ Quits the console, or the entire program if force is True """
        raise SystemExit(force)

def register_root(root):
    print('Application started.')
    print('Python: %s\nTk: %s' % (sys.version.split(' ')[0], TkVersion))
    def destroy_handler():
        print('Application quit.')
        root.destroy()
    root.protocol('WM_DELETE_WINDOW', destroy_handler)
