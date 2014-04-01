#!/usr/bin/env python
""" Team 830 scouting forms """

from __future__ import division, print_function

import csv
import math
import os
import pickle
import platform
import random
import re
import sys
import traceback
import zlib

PYTHON = int(sys.version.split('.')[0])  # either 2 or 3
try:
    # Python 2
    from Tkinter import *
    import Tkinter as tkinter
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
except ImportError:
    # Python 3
    from tkinter import *
    import tkinter
    import tkinter.messagebox as messagebox
    import tkinter.filedialog as filedialog

from lib.csvexport import CSVExporterBase
from lib.version import VERSION
import lib.validation as validation
import lib.debug as debug
import lib.urls as urls

# Form fields, in order
form_fields = [
    "match_num", "team_num", "auton_ball_num", "auton_high", "auton_low",
    "teleop_high", "teleop_high_miss", "teleop_low", "teleop_low_speed",
    "ranged_pass", "truss_pass", "fouls", "tech_fouls", "defense",
    "truss_catch", "range_catch", "human_catch", "match_result", "comments"
]

def initialize():
    """ Perform initialization

    Updates old installations
    """
    # Create data folder
    if not os.path.isdir('data'):
        if os.path.exists('data'):
            os.rename('data', 'data_%i' % hash(random.random()))
        os.mkdir('data')
    # Move old data files
    for f in os.listdir(os.getcwd()):
        if (f.startswith('data_') or f.endswith('_data.txt')
                or f.endswith('_data')):
            new_filename = os.path.join('data', f)
            while os.path.exists(new_filename):
                new_filename += '_'
            os.rename(f, new_filename)
    # Rename scouting_data.txt to scouting_data
    filename = os.path.join('data', 'scouting_data.txt')
    if os.path.exists(filename):
        os.rename(filename, os.path.join('data', 'scouting_data'))

def system_check():
    py_version = float('.'.join(sys.version.split('.')[:2]))
    if py_version >= 3 and py_version <= 3.2:
        messagebox.showwarning('Untested',
            'Python %f is not tested. Use at your own risk!' % py_version)
    if py_version == 2.6:
        messagebox.showwarning('Warning',
            'Python 2.6 is not tested as often as 2.7. Upgrade if you experience bugs.')
    if sys.platform == 'darwin' and platform.mac_ver()[0][:4] == '10.6':
        messagebox.showwarning('Warning',
            'If you experience interface problems, you may need to upgrade Tk.')

class IntegerEntry(Entry):
    def __init__(self, *args, **kwargs):
        self.max = kwargs.get('max', float('inf'))
        self.min = kwargs.get('min', float('-inf'))
        self.default = kwargs.get('default', 0)
        for v in ('max', 'min', 'default'):
            if v in kwargs:
                kwargs.pop(v)
        Entry.__init__(self, *args, **kwargs)
        self.validator = validation.IntegerEntryValidator(self)
        self.bind('<Key>', self.key_handler)

    def key_handler(self, event):
        if event.keysym in ('Up', 'Down'):
            self.increase(1 if event.keysym == 'Up' else -1)
            return 'break'
        elif event.keysym in ('Right', 'Left'):
            # Allow default
            pass
        else:
            return self.validator.keypress(event)

    def increase(self, value):
        try:
            val = int(self.get() or self.default)
        except ValueError:
            val = self.default
        val += value
        val = max(self.min, min(self.max, val))
        self.delete('0', END)
        self.insert('0', str(val))

class Form(object):
    """ Form data handler """
    # These properties are reserved for this class
    _reserved = ('data', '_reserved')
    def __init__(self):
        # Use object.__setattr__ instead of Form.__setattr__ to avoid recursion
        super(Form, self).__setattr__('data', {})

    def __setattr__(self, key, value):
        if key in self._reserved:
            raise AttributeError("Can't set %r attribute" % key)
        self.data[key] = value

    def __getattr__(self, key):
        if key in self._reserved:
            # Avoid recursion
            return super(Form, self).__getattr__(key)
        return self.data[key]

    def get_data(self):
        """ Returns the data from each field """
        d = {}  # dictionary
        for key in self.data:
            field = self.data[key]
            # Check field type
            if isinstance(field, Text):
                d[key] = field.get('0.0', END)
            elif isinstance(field, BooleanVar):
                # Convert to yes or no
                d[key] = 'yes' if int(bool(field.get())) else 'no'
            else:
                try:
                    d[key] = field.get()
                except TypeError as e:
                    raise TypeError('get() failed for field type %s: %s' %
                                    (field.__class__, e))
        return d

class MenuBar(Menu):
    def __init__(self, parent):
        Menu.__init__(self, parent)
        osx = (sys.platform == 'darwin')
        if osx:
            self.app_menu = Menu(self, name='apple')
            self.app_menu.add_command(label="About", command=about_window.show)
            self.add_cascade(menu=self.app_menu, label='')
            self.file_menu = Menu(self, tearoff=False)
        else:
            self.app_menu = self.file_menu = Menu(self, tearoff=False)
        self.file_menu.add_command(label='CSV export', underline=1,
            command=lambda: CSVExporter(root))
        if not osx:
            self.file_menu.add_separator()
            self.file_menu.add_command(label="About", command=about_window.show)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Exit", underline=1, command=self.quit)
        self.add_cascade(label="File", underline=0, menu=self.file_menu)
        parent['menu'] = self

    def quit(self):
        confirm = messagebox.askokcancel('Can I Ask You Something?', 'Are you sure you want to exit?')
        if confirm:
            exit_form()

#values:
#match_num, team_num, auton_ball_num, auton_high, auton_low, teleop_high
#teleop_high_miss, teleop_low, teleop_low_speed, ranged_pass
#truss_pass, fouls, tech_fouls, defense, truss_catch, range_catch, human_catch
#match_result, comments
class Application(Toplevel):
    """Application window for scouting sheet"""
    def __init__(self, master):
        """initialize the window"""
        Toplevel.__init__(self, master)
        self.logo = PhotoImage(file = "lib/logo.GIF")
        self.rainbow()
        self.form = Form()
        self.grid()
        self.create_fields()
        self.clear_entries()
        self.filename = os.path.join('data', "scouting_data")
        self.color_background('white')
        self.after_idle(self.check_data_file)

    def color_background(self, color=None):
        if color == 'random':
            color = "#" + ''.join([hex(random.randint(0, 15))[2:]
                                   for i in range(6)])
        self.config(background=color)
        for w in self.children.values():
            if isinstance(w, (Text, Entry)):
                w.config(highlightbackground=color)
            elif isinstance(w, (MenuBar, Toplevel)):
                pass
            else:
                try:
                    w.config(background=color, highlightbackground=color)
                except tkinter.TclError:
                    pass

    def rainbow(self):
        if self.rainbow_enabled:
            self.color_background('random')
        self.after(333, self.rainbow)

    rainbow_enabled = False
    def create_fields(self):
        """create input boxes and fields on the form"""
        # title
        Label(self, text="FRC team 830 - The RatPack").grid(row=0, column=0, columnspan=2, sticky=W)

        # match_num
        Label(self, text="Match #:").grid(row=1, column=0, sticky=W)
        self.form.match_num = IntegerEntry(self, min=0)
        self.form.match_num.grid(row=1, column=1, sticky=W)

        # team_num
        Label(self, text="Team #:").grid(row=1, column=2)
        self.form.team_num = IntegerEntry(self, min=0)
        self.form.team_num.grid(row=1, column=3, sticky=W, columnspan=1)

        # auton_ball_num
        Label(self, text="Auton balls posessed:") \
            .grid(row=2, column=0, sticky=W)
        self.form.auton_ball_num = IntegerEntry(self, min=0)
        self.form.auton_ball_num.grid(row=2, column=1, sticky=W)

        # auton_high
        Label(self, text="Auton High Goal").grid(row=2, column=2)
        scoring_options = ["N/A", "Missed", "Scored"]
        self.form.auton_high = StringVar()
        self.form.auton_high.set(None)
        for col, val in enumerate(scoring_options):
            Radiobutton(self, text=val, variable=self.form.auton_high,
                        value=val).grid(row=2, column=col + 3, sticky=E)

        # auton_low
        Label(self, text="Auton Low Goal").grid(row=3, column=2)
        self.form.auton_low = StringVar()
        self.form.auton_low.set(None)
        for col, val in enumerate(scoring_options):
            Radiobutton(self, text=val, variable=self.form.auton_low,
                        value=val).grid(row=3, column=col + 3, sticky=E)

        # teleop_high
        Label(self, text="Teleop High Goals:").grid(row=4, column=0, sticky=W)
        self.form.teleop_high = IntegerEntry(self, min=0)
        self.form.teleop_high.grid(row=4,column=1,sticky=W)

        # teleop_high_miss
        Label(self, text="High Goals Missed:").grid(row=4, column=2, sticky=W)
        self.form.teleop_high_miss = IntegerEntry(self, min=0)
        self.form.teleop_high_miss.grid(row=4, column=3, sticky=W, columnspan=1)

        # teleop_low
        Label(self, text="Teleop Low Goals:").grid(row=5, column=0, sticky=W)
        self.form.teleop_low = IntegerEntry(self, min=0)
        self.form.teleop_low.grid(row=5, column=1, sticky=W)

        # teleop_low_speed
        Label(self, text="Teleop Low Goal Speed:").grid(row=6 , column=0,
                                                columnspan=2, sticky=W)
        speed_options = ["N/A", "Slow", "Medium", "Fast"]
        self.form.teleop_low_speed = StringVar()
        self.form.teleop_low_speed.set(None)
        for col, val in enumerate(speed_options):
            Radiobutton(self, text=val, variable=self.form.teleop_low_speed,
                        value=val).grid(row=6, column=col + 1)

        # pass consistency
        Label(self, text=" ").grid(row=7, column=0, sticky=W)
        Label(self, text="Pass Consistency").grid(row=8, column=0, sticky=W)
        Label(self, text="N/A").grid(row=8, column=1, sticky=S)
        Label(self, text="Inconsistent").grid(row=8, column=2, sticky=S)
        Label(self, text="Consistent").grid(row=8, column=3, sticky=S)
        Label(self, text="Over Truss").grid(row=9, column=0, sticky=W)
        Label(self, text="Ranged Pass").grid(row=10, column=0, sticky=W)
        Label(self, text="").grid(row=11, column=0)

        # truss_pass
        pass_options = ["N/A", "Inconsistent", "Consistent"]

        self.form.truss_pass = StringVar()
        self.form.truss_pass.set(None)
        for col, val in enumerate(pass_options):
            Radiobutton(self, variable=self.form.truss_pass,
                        value=val).grid(row=9, column=col + 1)

        # ranged_pass
        self.form.ranged_pass = StringVar()
        self.form.ranged_pass.set(None)
        for col, val in enumerate(pass_options):
            Radiobutton(self, variable=self.form.ranged_pass,
                        value=val).grid(row=10, column=col + 1)

        # fouls
        Label(self, text="Fouls:").grid(row=12, column=0, sticky=E)
        self.form.fouls = IntegerEntry(self, min=0)
        self.form.fouls.grid(row=12, column=1, sticky=W)

        # tech_fouls
        Label(self, text="Technical Fouls:").grid(row=12, column=2, sticky=E)
        self.form.tech_fouls = IntegerEntry(self, min=0)
        self.form.tech_fouls.grid(row=12, column=3, sticky=W)
        Label(self, text="").grid(row=13, column=0)

        # defense
        defense_options = ["N/A", "Bad", "Mediocre", "Good"]
        Label(self, text="Defense:").grid(row=14, column=0, sticky=E)
        self.form.defense = StringVar()
        self.form.defense.set(None)
        for col, val in enumerate(defense_options):
            Radiobutton(self, variable=self.form.defense, value=val, text=val)\
                        .grid(row=14, column=col + 1)

        # catching: truss_catch, range_catch, human_catch
        Label(self, text="Catching:").grid(row=15, column=0, sticky=E)
        self.form.truss_catch = BooleanVar()
        self.form.range_catch = BooleanVar()
        self.form.human_catch = BooleanVar()
        Checkbutton(self, text="Truss", variable=self.form.truss_catch) \
            .grid(row=15, column=1, sticky=W)
        Checkbutton(self, text="Ranged", variable=self.form.range_catch) \
            .grid(row=16, column=1, sticky=W)
        Checkbutton(self, text="From Human", variable=self.form.human_catch) \
            .grid(row=17, column=1, sticky=W)

        # match_result
        result_options = ["Win", "Loss", "Tie"]
        Label(self, text="Match Result:").grid(row=15, column=2, sticky=E)
        self.form.match_result = StringVar()
        self.form.match_result.set(None)
        for row, val in enumerate(result_options):
            Radiobutton(self, variable=self.form.match_result, value=val,
                    text=val).grid(row=row + 15, column=3, sticky=W)
        Label(self, text="").grid(row=18, column=0)

        # comments
        Label(self, text="Comments:").grid(row=19, column=0)
        self.form.comments = Text(self, width=40, height=5, wrap=WORD,
                             background='#ccccff')
        self.form.comments.grid(row=19, column=1, columnspan=3, rowspan=2)

        # picture
        picture = Label(self, image=self.logo)
        picture.image = self.logo
        picture.grid(row=20, column=0)

        # submit button
        self.submit_button = Button(self, text="Submit Form",
                                    command = self.submit)
        self.submit_button.grid(row=20, column=4, sticky=E)
        def rb_stop():
            self.stop_button.grid_forget()
            self.rainbow_enabled = False

        self.stop_button = Button(self, text="Stop!", command=rb_stop)
        # Helper function to bind background clearing to field
        # Used for scoping - otherwise, field refers to the last field from loop
        def bind_to_field(field):
            # Helper function to handle key events
            def handler(event):
                if field.get():
                    field.config(background='white')
            field.bind('<KeyRelease>', handler, '+')
        # Lists of required fields
        self.entries = []
        self.radio_buttons = []
        for key in self.form.data:
            field = self.form.data[key]
            if isinstance(field, Entry):
                self.entries.append(field)
                bind_to_field(field)
            elif isinstance(field, StringVar):
                # Radio button
                self.radio_buttons.append(field)
    def check_submit(self):
        """ Checks to see if all required fields are filled out """
        color = "white"
        comments = self.form.comments.get("0.0", END).lower()
        if 'rainbow' in comments:
            self.rainbow_enabled = True
            self.stop_button.grid(row=21, column=4, sticky=E)
        valid = True
        for field in self.entries:
            # default background color
            field.config(background=color)
            if not field.get():
                #a field has not been completed
                field.config(background='#ffaaaa')
                valid = False
        for field in self.radio_buttons:
            if field.get() == 'None':
                valid = False
        return valid
    def submit(self, check=True):
        """ Reads values from scouting form and save to a file """
        def err():
            self.submit_button.config(state=DISABLED)
            messagebox.showerror("Can't submit form",
                'You need to fill in all fields before submitting.')
            self.submit_button.config(state=NORMAL)
        if check and not self.check_submit():
            self.update()
            self.after_idle(err)
            return False
        try:
            data = self.form.get_data()
            contents = self.load_data_file()
            # add data to end of list
            contents.append(data)
            self.save_data_file(contents)
            #clear entries
            self.clear_entries()
        except Exception as e:
            messagebox.showerror('Internal error', e)
        return True

    def clear_entries(self):
        """erase entries and give user a clean slate - Good as new!"""
        self.form.comments.delete("0.0", END)
        self.form.match_num.delete("0", END)
        self.form.team_num.delete("0", END)
        self.form.auton_ball_num.delete("0", END)
        self.form.auton_high.set('None')
        self.form.auton_low.set('None')
        self.form.teleop_high.delete("0", END)
        self.form.teleop_high_miss.delete("0", END)
        self.form.teleop_low.delete("0", END)
        self.form.teleop_low_speed.set('None')
        self.form.truss_pass.set('None')
        self.form.ranged_pass.set('None')
        self.form.fouls.delete("0", END)
        self.form.tech_fouls.delete("0", END)
        self.form.defense.set('None')
        self.form.truss_catch.set(False)
        self.form.range_catch.set(False)
        self.form.human_catch.set(False)
        self.form.match_result.set('None')

    def load_data_file(self, silent=False):
        """ Checks the data file for validity and loads its content

        silent: If true, raise an exception instead of prompting and clearing
            the data file
        """
        try:
            if os.path.exists(self.filename):
                f = open(self.filename, 'rb')
                content = f.read()
                # Decompress
                try:
                    content = zlib.decompress(content)
                except zlib.error:
                    # File is not zlib-compressed; skip decompression
                    pass
                # Unpickle
                if content:
                    data = pickle.loads(content)
                else:
                    data = []
                assert isinstance(data, list)
                f.close()
            else:
                # Create file
                self.save_data_file([])
                content = ''
                data = []
            return data
        except (IOError) as e:
            if silent:
                raise  # original exception
            messagebox.showerror('Error', 'Could not load data file: %s' % e)
            exit_form()
        except Exception as e:
            print(e)
            if not silent:
                # Data file is corrupt - either clear file or exit
                result = messagebox.askokcancel('Data file corrupt',
                    'The data file is corrupt. Press OK to clear the file '
                    'or cancel to quit.')
                if not result:
                    exit_form()
                # Overwrite data file (only if confirmed)
                self.save_data_file([])
                return []
            else:
                raise IOError('Unable to load data file')
        return False

    def check_data_file(self):
        """ load_data_file, without a return value """
        self.load_data_file()

    def save_data_file(self, data):
        if not isinstance(data, list):
            raise TypeError('data must be a list')
        with open(self.filename, 'wb') as f:
            # pickle - use protocol 2 for compatibility between Python 2 and 3
            content = pickle.dumps(data, protocol=2)
            # Compress
            try:
                content = zlib.compress(content)
            except zlib.error as e:
                # Log error but don't abort saving
                print('Failed to compress data: %s' % e)
            f.write(content)

class CSVExporter(CSVExporterBase):
    """ CSV export subclass """
    col_names = form_fields
    row_format = '#{id}: Match {data[match_num]}, team {data[team_num]}'
    def load_data(self):
        return app.load_data_file()
    def save_data(self, data):
        return app.save_data_file(data)

class AboutWindow(Toplevel):
    # Keep track of window
    urls = urls.get_urls()
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title('About')
        self.grid()
        self.columnconfigure(1, weight=1)
        self.columnconfigure(4, weight=1)
        self.draw()
        self.minsize(200, 0)
        self.bind('<Key>', self.keypress)
        self.protocol('WM_DELETE_WINDOW', self.withdraw)

    def show(self):
        # Force to front
        self.withdraw()
        self.deiconify()

    def draw(self):
        img = Label(self, image=app.logo)
        img.image = img
        img.grid(row=1, column=1, columnspan=4)
        Label(self, text='Python version:').grid(row=2, column=2, sticky=E)
        Label(self, text=sys.version.split(' ')[0]).grid(row=2, column=3, sticky=W)
        Label(self, text='Tk version:').grid(row=3, column=2, sticky=E)
        Label(self, text='%s' % TkVersion).grid(row=3, column=3, sticky=W)
        Label(self, text='Scouting form version:').grid(row=4, column=2, sticky=E)
        Label(self, text=VERSION).grid(row=4, column=3, sticky=W)
        Button(self, text='More info', command=lambda:self.open('wiki')) \
            .grid(row=10, column=2, columnspan=2)
        Button(self, command=lambda:self.open('bugreport'),
            text='Report a problem').grid(row=11, column=2, columnspan=2)

    def keypress(self, event):
        """ Handle keyboard input """
        if event.keysym == 'Escape':
            self.withdraw()

    def open(self, url):
        if url in self.urls:
            url = self.urls[url]
        try:
            import webbrowser
            webbrowser.open(url)
        except ImportError:
            messagebox.showerror('Module not found',
                                 'Could not open a web browser')

def exit_form():
    root.destroy()
    sys.exit()

if __name__ == '__main__':
    initialize()
    root = Tk()
    tkinter.CallWrapper = debug.ExceptionHandler.new_with_root(root)
    root.title("Aerial Assist Match Scouting Form")
    app = Application(root)
    about_window = AboutWindow(app)
    about_window.withdraw()
    menu = MenuBar(app)
    console = None
    open_console = ('--open-console' in sys.argv)
    root.config(menu=menu)
    root.withdraw()
    if '--debug' in sys.argv:
        console = debug.Console(root, globals())
        console.add_to_menubar(menu)
        debug.register_root(root)
        if open_console:
            root.update()
            root.after_idle(console.run_console)
    # Destroy root when app is closed
    app.protocol('WM_DELETE_WINDOW', root.destroy)
    root.after_idle(system_check)
    # Focus window on OS X
    if sys.platform == 'darwin':
        root.after_idle(os.system, './lib/osx_focus %i' % os.getpid())
    root.mainloop()
