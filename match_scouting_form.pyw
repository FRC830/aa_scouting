#!/usr/bin/env python
""" Team 830 scouting forms """
import csv
import math
import os
import pickle
import random
import sys
import zlib

PYTHON = int(sys.version.split('.')[0])  # either 2 or 3
try:
    # Python 2
    from Tkinter import *
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
except ImportError:
    # Python 3
    from tkinter import *
    import tkinter.messagebox as messagebox
    import tkinter.filedialog as filedialog

from lib.csvexport import CSVExporterBase
from lib.version import VERSION

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
    def __init__(self,parent):
        Menu.__init__(self,parent)
        fileMenu = Menu(self, tearoff=False)
        self.add_cascade(label="File", underline=0, menu=fileMenu)
        fileMenu.add_command(label='CSV export', underline=1,
            command=lambda: CSVExporter(root))
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", underline=1, command=self.quit)

#values:
#match_num, team_num, auton_ball_num, auton_high, auton_low, teleop_high
#teleop_high_miss, teleop_low, teleop_low_speed, ranged_pass
#truss_pass, fouls, tech_fouls, defense, truss_catch, range_catch, human_catch
#match_result, comments
class Application(Frame):
    """Application window for scouting sheet"""
    def __init__(self, master):
        """initialize the window"""
        Frame.__init__(self, master)
        self.form = Form()
        self.grid()
        self.create_fields()
        self.clear_entries()
        self.filename = os.path.join('data', "scouting_data")
        self.after(100, self.check_data_file)
        self.val_list=[self.match_num, self.team_num, self.auton_ball_num,
                       self.auton_high, self.auton_low, self.teleop_high,
                       self.teleop_high_miss, self.teleop_low, self.teleop_low_speed,
                       self.ranged_pass, self.truss_pass, self.fouls,
                       self.tech_fouls, self.defense, self.match_result]
    def create_fields(self):
        """create input boxes and fields on the form"""
        #title
        Label(self, text = "FRC team 830"
              ).grid(row=0, column=0, columnspan=2, sticky=W)
        #match_num input field
        Label(self, text="Match #:").grid(row=1, column=0, sticky=W)
        self.form.match_num = Entry(self)
        self.form.match_num.grid(row=1,column=1,sticky=W)
        #team_num input field
        Label(self, text="Team #:").grid(row=1, column=2)
        self.form.team_num = Entry(self)
        self.form.team_num.grid(row=1,column=3,sticky=W, columnspan=3)
        #auton_ball_num input field
        Label(self, text="Auton balls posessed:").grid(row=2, column=0, sticky=W)
        self.form.auton_ball_num = Entry(self)
        self.form.auton_ball_num.grid(row=2,column=1,sticky=W)
        #auton_high
        Label(self, text="Auton High Goal").grid(row=2, column=2)
        scoring_options=["N/A","Missed","Scored"]
        self.form.auton_high=StringVar()
        self.form.auton_high.set(None)
        col=3
        for val in scoring_options:
            Radiobutton(self, text = val, variable = self.form.auton_high, value=val
                        ).grid(row = 2, column=col, sticky=E)
            col+=1
        #auton_low
        Label(self, text="Auton Low Goal").grid(row=3, column=2)
        scoring_options=["N/A","Missed","Scored"]
        self.form.auton_low=StringVar()
        self.form.auton_low.set(None)
        col=3
        for val in scoring_options:
            Radiobutton(self, text = val, variable = self.form.auton_low, value=val
                        ).grid(row = 3, column=col, sticky=E)
            col+=1
        #teleop_high
        Label(self, text="Teleop High Goals:").grid(row=4, column=0, sticky=W)
        self.form.teleop_high = Entry(self)
        self.form.teleop_high.grid(row=4,column=1,sticky=W)
        #teleop_high_miss
        Label(self, text="High Goals Missed:").grid(row=4, column=2, sticky=W)
        self.form.teleop_high_miss = Entry(self)
        self.form.teleop_high_miss.grid(row=4,column=3,sticky=W, columnspan=3)
        #teleop_low
        Label(self, text="Teleop Low Goals:").grid(row=5, column=0, sticky=W)
        self.form.teleop_low = Entry(self)
        self.form.teleop_low.grid(row=5,column=1,sticky=W)
        #teleop_low_speed
        Label(self, text="Teleop Low Goal Speed:").grid(row=6 , column=0,
                                                       columnspan=2, sticky=W)
        speed_options=["N/A", "Slow", "Medium", "Fast"]
        self.form.teleop_low_speed = StringVar()
        self.form.teleop_low_speed.set(None)
        col = 1
        for val in speed_options:
            Radiobutton(self, text=val, variable=self.form.teleop_low_speed, value=val
                        ).grid(row=6, column=col)
            col+=1

        #pass consistency
        Label(self, text = " ").grid(row=7, column=0, sticky=W)
        Label(self, text = "Pass Consistency").grid(row=8, column=0, sticky=W)
        Label(self, text = "N/A").grid(row=8, column=1, sticky=S)
        Label(self, text = "Inconsistent").grid(row=8, column=2, sticky=S)
        Label(self, text = "Consistent").grid(row=8, column=3, sticky=S)
        Label(self, text = "Over Truss").grid(row=9, column=0, sticky=W)
        Label(self, text = "Ranged Pass").grid(row=10, column=0, sticky=W)
        Label(self, text = " ").grid(row=11, column=0)
        pass_options = ["N/A", "Inconsistent", "Consistent"]
        #ranged_pass
        self.form.ranged_pass = StringVar()
        self.form.ranged_pass.set(None)
        col = 1
        for val in pass_options:
            Radiobutton(self, variable = self.form.ranged_pass, value = val
                        ).grid(row=10, column=col)
            col+=1
        #truss_pass
        self.form.truss_pass = StringVar()
        self.form.truss_pass.set(None)
        col = 1
        for val in pass_options:
            Radiobutton(self, variable = self.form.truss_pass, value = val
                        ).grid(row=9, column=col)
            col+=1
        #ranged_pass
        self.ranged_pass = StringVar()
        self.ranged_pass.set(None)
        col = 1
        for val in pass_options:
            Radiobutton(self, variable = self.ranged_pass, value = val
                        ).grid(row=10, column=col)
            col+=1
        #fouls
        Label(self, text="Fouls:").grid(row=12, column=0, sticky=E)
        self.form.fouls=Entry(self)
        self.form.fouls.grid(row=12, column=1, sticky=W)
        #tech_fouls
        Label(self, text="Technical Fouls:").grid(row=12, column=2, sticky=E)
        self.form.tech_fouls=Entry(self)
        self.form.tech_fouls.grid(row=12, column=3, sticky=W)
        Label(self, text = " ").grid(row=13, column=0)
        #defense
        Label(self, text="Defense:").grid(row=14, column=0, sticky=E)
        col=1
        defense_options = ["N/A", "Bad", "Mediocre", "Good"]
        self.form.defense = StringVar()
        self.form.defense.set(None)
        for val in defense_options:
            Radiobutton(self, variable=self.form.defense, value=val, text=val
                        ).grid(row=14, column=col)
            col+=1
        #catching: truss_catch, range_catch, human_catch
        Label(self, text="Catching:").grid(row=15, column=0, sticky=E)
        self.form.truss_catch = BooleanVar()
        self.form.range_catch = BooleanVar()
        self.form.human_catch = BooleanVar()
        Checkbutton(self, text="Truss", variable=self.form.truss_catch).grid(
            row=15, column=1, sticky=W)
        Checkbutton(self, text="Ranged", variable=self.form.range_catch).grid(
            row=16, column=1, sticky=W)
        Checkbutton(self, text="From Human", variable=self.form.human_catch).grid(
            row=17, column=1, sticky=W)
        #match_result
        Label(self, text="Match Result:").grid(row = 15, column=2, sticky=E)
        result_options = ["Win", "Loss", "Tie"]
        self.form.match_result = StringVar()
        self.form.match_result.set(None)
        row=15
        for val in result_options:
            Radiobutton(self, variable=self.form.match_result, value=val, text=val
                        ).grid(row=row, column=3, sticky=W)
            row+=1
        Label(self, text=" ").grid(row=18, column=0)
        #comments
        Label(self, text="Comments:").grid(row=19, column=0)
        self.form.comments = Text(self, width = 40, height=5, wrap=WORD,
                             background='#ffff00')
        self.form.comments.grid(row=19, column=1, columnspan=3, rowspan=2)
        #picture
        logo = PhotoImage(file = "lib/logo.GIF")
        picture = Label(self, image=logo)
        picture.image = logo
        picture.grid(row=20, column=0)
        #submit button
        Button(self, text="Submit Form", command = self.check_submit) \
            .grid(row=20, column=4, sticky=E)
        # Helper function to bind background clearing to field
        # Used for scoping - otherwise, field refers to the last field from loop
        def bind_to_field(field):
            # Helper function to handle key events
            def handler(event):
                if field.get():
                    field.config(background='white')
            field.bind('<KeyRelease>', handler)
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
        """checks if required fields are filled, if so it submits"""
        valid = True
        for field in self.entries:
            # default background color
            field.config(background='white')
            if not field.get():
                #a field has not been completed
                field.config(background='#ffaaaa')
                valid = False
        for field in self.radio_buttons:
            if field.get() == 'None':
                valid = False
        if valid:
            self.submit()
    def submit(self):
        """Read values from scouting form and save to a file"""
        try:
            data = self.form.get_data()
            contents = self.load_data_file()
            # add data to end of list
            contents.append(data)
            self.save_data_file(contents)
            #clear entries
            self.clear_entries()
        except Exception as e:
            messagebox.showinfo('Internal error', e)

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
            sys.exit()
        except Exception as e:
            print(e)
            if not silent:
                # Data file is corrupt - either clear file or exit
                result = messagebox.askokcancel('Data file corrupt',
                    'The data file is corrupt. Press OK to clear the file '
                    'or cancel to quit.')
                if not result:
                    sys.exit()
                # Overwrite data file (only if confirmed)
                self.save_data_file([])
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

if __name__ == '__main__':
    initialize()
    root = Tk()
    root.title("Aerial Assist Match Scouting Form")
    app = Application(root)
    menu = MenuBar(root)
    root.config(menu=menu)
    root.mainloop()
