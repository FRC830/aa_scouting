""" Debugging """

from __future__ import print_function

import code, os, sys, traceback, inspect, datetime
PYTHON = int(sys.version.split('.')[0])

try:
    # Python 2
    from Tkinter import *
    import tkMessageBox as messagebox
    from StringIO import StringIO
except ImportError:
    # Python 3
    from tkinter import *
    import tkinter.messagebox as messagebox
    from io import StringIO

import lib.urls as urls

def restart():
    """ Restarts the whole program """
    if messagebox.askyesno('Restart', 'Are you sure you want to restart? '
                        'No data will be saved.'):
        os.execl(sys.executable, sys.executable, *sys.argv)

class Console:
    # Restricted variables that shouldn't be accessible
    restricted = ('help',)

    class Menubar(Menu):
        def __init__(self, master, console):
            Menu.__init__(self, master)
            master['menu'] = self

            self.add_cascade(label='Application',
                             menu=console.master.cget('menu'))

            self.console_menu = Menu(self, tearoff=False)
            self.add_cascade(menu=self.console_menu, label='Console')
            self.console_menu.add_command(label='Clear',
                command=console.clear_output)
            self.console_menu.add_command(label='Cancel input',
                command=console.cancel_input)

            self.tool_menu = Menu(self, tearoff=False)
            self.add_cascade(menu=self.tool_menu, label='Tools')
            self.tool_menu.add_command(label='Restart', command=restart)

    def __init__(self, master, cvars=None):
        self.master = master
        if cvars is None:
            cvars = {}
        for var in self.restricted:
            # Deleting doesn't work with help(), but setting it explicitly does
            cvars[var] = None
        self.globals = cvars
        self.globals['quit'] = self.globals['exit'] = self.quit
        self.globals['self'] = self
        self.globals['clear'] = self.clear_output
        self.window = Toplevel(master)
        self.window.grid()
        self.window.title('Debug console')
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.protocol('WM_DELETE_WINDOW', self.window.withdraw)

        self.out = Text(self.window, width=80, height=24)
        self.out.insert(0.0, '''Application started.
            Python: %s\nTk: %s
            >>> '''.replace('  ', '') % (sys.version.split(' ')[0], TkVersion))
        self.out.config(state=DISABLED, highlightthickness=0)
        self.out.grid(row=1, column=1, sticky='nsew')
        self.out.bind('<1>', lambda event: self.out.focus_set())
        out_scrollbar = Scrollbar(self.window)
        out_scrollbar.grid(row=1, column=2, sticky='ns')
        out_scrollbar.config(command=self.out.yview)
        self.out.config(yscrollcommand=out_scrollbar.set)

        self.status = Label(self.window, text='Opened console',
                            background='#eee', anchor=W)
        self.status.grid(row=2, column=1, columnspan=100, sticky=E+W)
        self.input = Text(self.window, width=80, height=2)
        self.input.grid(row=3, column=1, columnspan=100, sticky='ew')
        self.input.bind('<Key>', self.input_keypress)
        self.console = code.InteractiveConsole(self.globals)
        self.buffer = StringIO()
        self.console.write = self.buffer.write  # Handles stderr

        self.menu = self.Menubar(self.window, self)
        self.window.config(menu=self.menu)
        self.window.withdraw()

    def add_to_menubar(self, menubar):
        menu = Menu(menubar, tearoff=False)
        menubar.add_cascade(label='Debug', menu=menu)
        menu.add_command(label='Console', command=self.run_console)
        menu.add_separator()
        menu.add_command(label='Restart', command=restart)

    def run_console(self):
        self.window.withdraw()
        self.window.deiconify()
        self.input.focus_set()

    def cancel_input(self):
        self.console.push(';')
        self.eval()
        self.out.config(state=NORMAL)
        self.out.insert(END, '\nCancelled input.\n>>> ')
        self.out.config(state=DISABLED)

    def clear_output(self):
        prompt = self.out.get('0.0', END)[-5:-1]
        self.out.config(state=NORMAL)
        self.out.delete('0.0', END)
        self.out.insert('0.0', prompt)
        self.out.config(state=DISABLED)

    def input_keypress(self, event):
        if event.keysym == 'Return':
            self.eval()
            return 'break'

    def eval(self):
        try:
            line = self.input.get('0.0', END).rstrip('\n')
            if PYTHON == 2:
                line = bytes(line)
        except UnicodeEncodeError:
            messagebox.showerror('Unicode error', 'Could not encode input')
            return
        self.input.delete('0.0', END)
        last_end = self.buffer.tell()

        status = '<Console>'
        sys.stdout = self.buffer
        sys.stderr = self.buffer
        print(line)
        if self.console.push(line):
            sys.stdout.write('... ')
            status += ' continue input'
        else:
            sys.stdout.write('>>> ')
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        self.status.config(text=status)
        self.out.config(state=NORMAL)
        self.buffer.seek(last_end)
        self.out.insert(END, self.buffer.read())
        self.out.see(END)
        self.out.config(state=DISABLED)

    def quit(self, force=False):
        """ Quits the console, or the entire program if force is True """
        if force:
            raise SystemExit
        else:
            self.window.withdraw()

class ExceptionHandler:
    """ Handles uncaught exceptions in Tkinter callbacks """
    def __init__(self, root, func, subst, widget):
        self.root = root
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except Exception:
            info = ''
            try:
                tb = traceback.format_exc()
                info += tb + '\n------\n'
                info += str(inspect.getargvalues(sys.exc_info()[2].tb_frame))
            except Exception as e:
                info += '\nERROR: %s' % e
            try:
                ExceptionReporter(self.root, tb, info)
            except Exception:
                print('Unable to display exception reporter')
                traceback.print_exc()

    @staticmethod
    def new_with_root(root):
        def wrapper(*args):
            return ExceptionHandler(root, *args)
        return wrapper

class ExceptionReporter(Toplevel):
    def __init__(self, master, tb, dump):
        Toplevel.__init__(self, master)
        self.tb = tb.replace(os.getcwd(), '.')
        self.title('Internal error')
        self.grid()
        self.columnconfigure(1, weight=1)
        path = self.save_dump(dump)
        self.tb += '\nSaved to: %s' % path
        self.draw()
        self.minsize(200, 0)
        self.after_idle(self.lift)

    def draw(self):
        Label(self, text='An internal error has occurred.').grid(row=1, column=1, sticky=W)
        text = self.text = Text(self, width=80, height=20, wrap=WORD)
        text.grid(row=2, column=1, columnspan=2)
        text.insert('0.0', self.tb)
        # Disable widget, but make clicking set focus so copying works
        text.config(state=DISABLED)
        text.bind('<1>', lambda event: text.focus_set())
        # Auto-focus
        text.focus_set()
        text.tag_add('sel', '0.0', END)
        Label(self, text='Copy this text and submit a bug report, if necessary')\
            .grid(row=3, column=1, columnspan=2, sticky=W)
        self.copy_button = Button(self, text='Copy to clipboard',
                                  command=self.copy, width=20)
        self.copy_button.grid(row=4, column=2, sticky=W)
        self.copy_button.bind('<Leave>',
            lambda event: self.copy_button.config(text='Copy to clipboard'))
        Button(self, text="Don't submit", command=self.destroy) \
            .grid(row=5, column=1, sticky=W)
        Button(self, text='Submit report',
               command=lambda: urls.open('newissue')) \
            .grid(row=5, column=2, sticky=E)

    def save_dump(self, dump):
        filename = 'data/dump_%s.txt' % \
                   datetime.datetime.today().strftime('%d_%m_%Y_%H_%M_%S')
        with open(filename, 'ab') as f:
            try:
                f.write(dump)
            except Exception as e:
                print('Could not write to file: %s' % e)
        return filename

    def copy(self):
        """ Copies text to clipboard """
        try:
            self.text.tag_add('sel', '0.0', END)
            self.text.clipboard_clear()
            self.text.clipboard_append('```\n')
            self.text.clipboard_append(self.text.get('sel.first', 'sel.last'))
            self.text.clipboard_append('\n```')
            self.copy_button.config(text='Copied!')
        except Exception:
            self.copy_button.config(text='Failed')

def register_root(root):
    def destroy_handler():
        print('Application quit.')
        root.destroy()
    root.protocol('WM_DELETE_WINDOW', destroy_handler)
