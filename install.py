#!/usr/bin/env python
import sys
import os

if sys.version < '2.2':
	sys.exit('Error: Python-2.2 or newer is required. Current version:\n %s'
			% sys.version)

try:
	import gtk
	import gtk.glade
except:
	sys.exit('Error: gtk and gtk.glade are required')

try:
	import pygtk
	pygtk.require("2.0")
except:
	sys.exit('Error: pygtk 2.0 is required')



if not os.path.exists('/usr/share/gcue2tracks/'):
	os.system('sudo mkdir /usr/share/gcue2tracks/')

os.system('sudo cp gCue2tracks.desktop /usr/share/applications')
os.system('sudo cp gCue2tracks.png /usr/share/pixmaps')
os.system('sudo cp gCue2tracks.glade /usr/share/gcue2tracks/gCue2tracks.glade')
os.system('sudo cp gCue2tracks.png /usr/share/gcue2tracks')
os.system('sudo cp gCue2tracks /usr/bin')
os.system('sudo cp menu/gCue2tracks /usr/share/menu')
os.system('sudo cp gCue2tracks.py /usr/share/gcue2tracks/gCue2tracks.py')
os.system('sudo cp config.py /usr/share/gcue2tracks')
os.system('sudo cp decoder.py /usr/share/gcue2tracks')





