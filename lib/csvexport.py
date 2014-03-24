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
    """ Base CSV Exporter class

    Do not instantiate this directly - instead, make a subclass and specify:
    * col_names: A list of column names (must exist, but content is optional)
    * get_data: A function that returns data to save (a list of dicts)
    """
    window_title = 'CSV export'
    row_format = 'Row #{id}: {data}'
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title(self.window_title)
        self.grid()
        # Set columns 1 and 5 to resize with window
        self.columnconfigure(1, weight=1)
        self.columnconfigure(5, weight=1)
        self.draw()
        self.bind('<Key>', self.keypress)
        # geometry is width x height + x + y
        position = tuple(int(x) + 20 for x in master.geometry().split('+', 1)[1].split('+'))
        self.geometry('+%i+%i' % position)

    def draw(self):
        """ Draws widgets """
        Label(self, text='Data to export:').grid(row=1, column=2, columnspan=3)
        self.list = listbox = Listbox(self, selectmode=MULTIPLE)
        listbox.grid(row=2, column=1, columnspan=5, padx=15, sticky=E+W)
        self.draw_listbox()

        self.save_clear_data = BooleanVar()
        Checkbutton(self, text='Remove rows after saving',
            variable=self.save_clear_data).grid(row=3, column=2, columnspan=3)
        self.save_clear_data.set(True)

        def select_all():
            listbox.selection_set(0, END)
        def select_none():
            listbox.selection_clear(0, END)
        select_all()  # Start with everything selected

        Button(self, text='Select all',
               command=select_all).grid(row=4, column=2)
        Button(self, text='Select none',
            command=select_none).grid(row=4, column=3)
        Button(self, text='Refresh', command=self.draw_listbox).grid(row=5, column=2)
        Button(self, text='Cancel', command=self.destroy).grid(row=5, column=3)
        submit = Button(self, text='Export', command=self.export)
        submit.grid(row=5, column=4)
        submit.config(default='active')
        def nodata():
            # Displays "no data" error
            self.destroy()
            messagebox.showerror('No data', 'No data to export!'),
        if not len(self.data):
            # Display error after idle, to make sure dialog displays correctly
            self.after_idle(nodata)

    def draw_listbox(self):
        # Store old selection and clear list
        old_selection = [int(x) for x in self.list.curselection()]
        old_len = self.list.size()
        self.list.delete(0, END)
        self.data = self.__load_data()
        for i, d in enumerate(self.data):
            self.list.insert(END, self.row_format.format(id=i+1, data=d))
            if i in old_selection or i >= old_len:
                # This row was selected before or is new
                self.list.selection_set(i, i)

    def keypress(self, event):
        """ Handles keyboard input to window """
        if event.keysym == 'Escape':
            self.destroy()
        if event.keysym == 'Return':
            self.export()

    def export(self):
        """ Prompts for a location and exports CSV data """
        # Generate data & check
        rows = [self.data[int(x)] for x in self.list.curselection()]
        if not len(rows):
            messagebox.showerror("Error", "No data to export")
            return
        # Dialog should prevent overwriting an existing file accidentally
        filename = filedialog.asksaveasfilename(defaultextension='.csv')
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
            writer = csv.writer(csvfile, lineterminator='\n')
            # Column headers
            writer.writerow(self.process_column_names(col_names))
            for r in rows:
                # If a column doesn't exist in a row, leave it blank
                row_values = [(r[col_names[i]] if col_names[i] in r else '')
                    for i in range(len(col_names))]
                writer.writerow(row_values)
        if self.save_clear_data.get():
            # Remove exported rows
            keep_rows = [r for r in self.data if r not in rows]
            self.__save_data(keep_rows)
        # Close when done
        self.destroy()

    def process_column_names(self, names):
        """ Make column names more human-readable """
        return list(map(
            lambda n: n.replace('_', ' ').replace('num', 'number').capitalize(),
        names))

    def __load_data(self):
        if hasattr(self, 'load_data') and hasattr(self.load_data, '__call__'):
            return self.load_data()
        else:
            raise NotImplementedError('load_data should be implemented in a subclass')

    def __save_data(self, data):
        if hasattr(self, 'save_data') and hasattr(self.save_data, '__call__'):
            return self.save_data(data)
        else:
            raise NotImplementedError('save_data should be implemented in a subclass')

    def __get_col_names(self):
        if hasattr(self, 'col_names'):
            return self.col_names
        else:
            raise NotImplementedError('col_names should be declared in a subclass')
