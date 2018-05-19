import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Notes:
#
# **** Signal handling *****
#
# To connect a signal
#   handler_id = widget.connect("event", callback, data)
# To remove that signal:
#   widget.disconnect(handler_id) or widget.disconnect_by_func(callback)

fake_date = [
  {
    'id': 1,
    'primary': 'python-gtk',
    'tags': ['python','gtk','gui'],
    'clue': 'signals',
    'answer': 'Use handler_id = widget.connect("event", callback, data)'
  },
  {
    'id': 2,
    'primary': 'python-gtk',
    'tags': ['python','gtk','gui'],
    'clue': 'signals remove',
    'answer': 'Use widget.disconnect(handler_id)'
  },
  {
    'id': 3,
    'primary': 'bash',
    'tags': [],
    'clue': 'set -u',
    'answer': 'Does cool stuff'
  }
]

class MyWindow(Gtk.Window):

  def make_box(data):
    box = Gtk.Box(spacing = 6)
    box.pack_start(Gtk.Label(label='ID'))

  def __init__(self):
    Gtk.Window.__init__(self, title="Hello World")

    id_label = Gtk.Label(label='ID')
    self.add(id_label)


    self.button = Gtk.Button(label='Click here')
    self.button.connect('clicked', self.button_handler)
    self.add(self.button)

  def button_handler(self, widget):
    print('Button click')


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
