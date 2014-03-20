""" CSV exporting """
import sys, csv
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

class CSVExporterBase(Toplevel):
    window_title = 'CSV export'
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title(self.window_title)
        self.grid()
        self.draw()

    def draw(self):
        Label(self, text='Data to export:').grid(row=1, column=1, columnspan=3)
        self.list = listbox = Listbox(self, selectmode=MULTIPLE)
        listbox.grid(row=2, column=1, columnspan=3, padx=25)
        self.data = self.__get_data()
        for i, d in enumerate(self.data):
            listbox.insert(END,
                '#%i: Match %s, team %s' % (i+1, d['match_num'], d['team_num']))

        def select_all():
            listbox.selection_set(0, END)
        def select_none():
            listbox.selection_clear(0, END)
        select_all()  # Start with everything selected

        Button(self, text='Select all',
               command=select_all).grid(row=3, column=1)
        Button(self, text='Select none',
            command=select_none).grid(row=3, column=2)
        Button(self, text='Refresh', command=self.draw).grid(row=4, column=1)
        Button(self, text='Cancel', command=self.destroy).grid(row=4, column=2)
        Button(self, text='Export', command=self.export).grid(row=4, column=3)
        if not len(self.data):
            messagebox.showerror('No data', 'No data to export!')
            self.destroy()

    def export(self):
        # Generate data & check
        rows = [self.data[int(x)] for x in self.list.curselection()]
        if not len(rows):
            messagebox.showinfo("Error", "No data to export")
            return
        # Dialog should prevent overwriting an existing file accidentally
        filename = filedialog.asksaveasfilename(defaultextension='csv')
        if not filename:
            return
        # Column names, used to sort data (dictionaries aren't sorted)
        col_names = self.__get_col_names()
        for k in rows[0].keys():
            # Add any column names not in form_fields.
            # Note that these fields will not necessarily be in the same order
            # across different CSV files, so declaring them in form_fields is
            # a good idea.
            if k not in col_names:
                col_names.append(k)
        # Options for open()
        opts = {}
        if PYTHON == 3:
            # Use utf-8 with Python 3
            opts['encoding'] = 'utf-8'
        with open(filename, 'w', **opts) as csvfile:
            writer = csv.writer(csvfile)
            # Column headers
            writer.writerow(self.process_column_names(col_names))
            for r in rows:
                # If a column doesn't exist in a row, leave it blank
                row_values = [(r[col_names[i]] if col_names[i] in r else '')
                    for i in range(len(col_names))]
                writer.writerow(row_values)
        # Close when done
        self.destroy()

    def process_column_names(self, names):
        """ Make column names more human-readable """
        return list(map(
            lambda n: n.replace('_', ' ').replace('num', 'number').capitalize(),
        names))

    def __get_data(self):
        if hasattr(self, 'get_data') and hasattr(self.get_data, '__call__'):
            return self.get_data()
        else:
            raise NotImplementedError('get_data should be implemented in a subclass')

    def __get_col_names(self):
        if hasattr(self, 'col_names'):
            return self.col_names
        else:
            raise NotImplementedError('col_names should be declared in a subclass')


