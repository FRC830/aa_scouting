""" Form validation """

class Validator(object):
    """ Base validator class """
    pass

class EntryValidator(Validator):
    def __init__(self, *args):
        self.fields = []
        self.bind_to(*args)

    def bind_to(self, *fields):
        for f in fields:
            f.bind('<Key>', self.keypress)
            self.fields.append(f)

    def keypress(self, event):
        field = event.widget
        if event.keysym in ('BackSpace', 'Tab'):
            return True
        if not self.is_valid(event.keysym):
            return 'break'  # stop event
        return True

    def is_valid(self, input):
        raise NotImplementedError

class IntegerEntryValidator(EntryValidator):
    def is_valid(self, input):
        try:
            int(input)
            return True
        except ValueError:
            return False

