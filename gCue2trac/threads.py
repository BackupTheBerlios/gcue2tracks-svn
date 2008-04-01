#!/usr/bin/env python

""" Simple pyGTK multithreading example"""

# Adapted from a post by Alif Wahid on the pyGTK mailinglist.
# Cedric Gustin, August 2003

import sys
import time
import gtk
import popen2
from threading import Thread

threadcount=0

class Test (Thread):
    def __init__ (self,button, count=0):
        Thread.__init__(self)
        self.count = count
        self.button=button

    def run (self):
		for i in range(0,1):
			time.sleep(1)
			# Acquire and release the lock each time.
			gtk.threads_enter()
			proc1 = popen2.Popen3('cd /usr/src/linux/ ;find  -type f -name "p*"')
			fromchild = proc1.fromchild.readline()
			print fromchild
			while fromchild:
				fromchild = proc1.fromchild.readline()
				print fromchild

			self.button.set_label("Thread %002d - %d" % (self.count,i))
			gtk.threads_leave()
		gtk.threads_enter()
		self.button.set_label("  Start Thread  ")
		gtk.threads_leave()

def start_new_thread (button, data=None):
    global threadcount
    threadcount += 1
    a = Test(button,threadcount)
    a.start()


def hello(*args):
    """ Callback function that is attached to the button """
    print "Hello World"
    window.destroy()

def destroy(*args):
    """ Callback function that is activated when the program is destoyed
"""
    window.hide()
    gtk.main_quit()

# Initialize threads
gtk.threads_init()

window = gtk.Window(gtk.WINDOW_TOPLEVEL)
window.connect("destroy", destroy)
window.set_border_width(10)

button = gtk.Button("  Start Thread  ")
button.connect("clicked", start_new_thread,button)
window.add(button)
button.show()

window.show_all()
gtk.threads_enter()
gtk.main()
gtk.threads_leave()
