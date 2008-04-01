#!/usr/bin/env python
  
  
#       
#       
#       Copyright 2008 test <test@dicson>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


import os, threading, locale

import pygtk
pygtk.require('2.0')
import gtk
import gobject

encoding = locale.getlocale()[1]
utf8conv = lambda x : unicode(x, encoding).encode('utf8')

sw = gtk.ScrolledWindow()
sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
textview = gtk.TextView()
textbuffer = textview.get_buffer()
sw.add(textview)

def on_button_clicked(button, buffer):
    command = 'cue2tracks -c ' + 'ogg' + ' -Q7 -f cp1251 -R ' + '"' + '/home/test/Desktop/Андрей Макаревич - У ломбарда/Андрей Макаревич - У ломбарда.cue' + '"'
    thr = threading.Thread(target= read_output, args=(command, buffer))
    thr.run()

def read_output(oscommand, txtbuffer):
    stdin, stdouterr = os.popen4(oscommand)
    for line in stdouterr.readlines():
        txtbuffer.insert(txtbuffer.get_end_iter(), utf8conv(line))

win = gtk.Window()
win.resize(300,500)
win.connect('delete-event', gtk.main_quit)
button = gtk.Button(u"Press me!")
button.connect("clicked", on_button_clicked, textbuffer)
vbox = gtk.VBox()
vbox.pack_start(button, False)
vbox.pack_start(sw)
win.add(vbox)
win.show_all()

gtk.main()
