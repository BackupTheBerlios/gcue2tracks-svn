#!/usr/bin/env python

import sys
import os
import threading
import popen2
import time
import subprocess
import gobject
from threading import Thread
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
  	import gtk.glade
except:
	sys.exit(1)
	
fileselect=""
a=""
def proc(n):	###########################
	pyWine.proc1 = popen2.Popen3('cd / ;find  -type f -name "p*"')
#	pyWine.proc1.setDaemon(True)
	fromchild = pyWine.proc1.fromchild.readline()
	sys.stdout.write(fromchild + '\n')
	while fromchild:
		fromchild = pyWine.proc1.fromchild.readline().decode('utf-8')
		sys.stdout.write(fromchild + '\n')
		buff=pyWine.textbuffer.get_text(pyWine.textbuffer.get_start_iter(),pyWine.textbuffer.get_end_iter(), include_hidden_chars=False)
		#pyWine.textbuffer.set_text( buff+fromchild+ '\n')
#p1 = threading.Thread(target=proc, name="t1", args=["1"])

def log(n):
	time.sleep(1)
	print "dddddddddddddddddddddddddddd"
	fromchild = pyWine.proc1.fromchild.readline()
	sys.stdout.write(fromchild + '\n')
	while fromchild:
		fromchild = pyWine.proc1.fromchild.readline()
		sys.stdout.write(fromchild + '\n')
		pyWine.textbuffer.set_text(fromchild + '\n')
		
class Test (Thread):

    def run (self):
		pyWine.proc1 = popen2.Popen3('cd /usr/src/linux/ ;find  -type f -name "p*"')
		fromchild = pyWine.proc1.fromchild.readline()
		sys.stdout.write(fromchild + '\n')
		while fromchild:
			fromchild = pyWine.proc1.fromchild.readline().decode('utf-8')
			sys.stdout.write(fromchild + '\n')
			buff=pyWine.textbuffer.get_text(pyWine.textbuffer.get_start_iter(),pyWine.textbuffer.get_end_iter(), include_hidden_chars=False)
			pyWine.textbuffer.set_text( buff+fromchild+ '\n')		
		
class MyThread(threading.Thread):

     def run(self):
		#self.setDaemon(True)
		#time.sleep(10)
		pyWine.proc1 = popen2.Popen3('cd /usr/src/linux/ ;find  -type f -name "p*"')
	#	pyWine.proc1 = subprocess.Popen(['cd /usr/src/linux/ ;find  -type f -name "p*"'], shell=True, stdin=subprocess.PIPE, 
	#			stdout=subprocess.PIPE, close_fds=True)
		#output = pyWine.proc1.stdout.readline()
		#while output:
			#output = pyWine.proc1.stdout.readline()
			#print output
		#pyWine.proc1.setDaemon(True)
		fromchild = pyWine.proc1.fromchild.readline()
		sys.stdout.write(fromchild + '\n')
		while fromchild:
			fromchild = pyWine.proc1.fromchild.readline().decode('utf-8')
			fromchild.replace('\033',' ',6)
			sys.stdout.write(fromchild + '\n')
			buff=pyWine.textbuffer.get_text(pyWine.textbuffer.get_start_iter(),pyWine.textbuffer.get_end_iter(), include_hidden_chars=False)
			pyWine.textbuffer.set_text( buff+fromchild+ '\n')
				
class MyThread1(threading.Thread):

     def run(self):
 #    	MyThread().setDaemon(True)
		MyThread().start()
		MyThread().run()
		#time.sleep(1)
		MyThread().join()
		print 'Thread', self.getName(), 'ended.'
class pyWine:

	def __init__(self):
		"""
		This start the gui in a asynchronous thread. We are in the "main" thread of the application, wich will later be used by the gui as well. We spawn a new thread for the worker.

		"""
		
		#self.qIn=Queue.Queue()
		#self.qOut=Queue.Queue()
		#self.gui=GuiPart(self.qIn,self.qOut)
		#self.running=True
		#self.incomingThread=threading.Thread(target=self.processIncoming)
		#print "plop=",self.incomingThread
		#self.incomingThread.setDaemon(True)
		#self.incomingThread.start()
		 #print "pika=",pika
		#gtk.threads_enter()
		#gtk.main()
		#self.running=False
		#gtk.threads_leave()################################################################
		#proc1 = '\n'
		#Set the Glade file
		self.gladefile = "pywine.glade"  
		self.wTree = gtk.glade.XML(self.gladefile, "mainWindow") 
		combobox = self.wTree.get_widget("combobox1")
		iter=combobox.set_active(0)	
		#Create our dictionay and connect it
		dic = {"on_mainWindow_destroy" : gtk.main_quit
				, "on_AddWine" : self.OnAddWine, "onf" : self.onf, "start_recomp" : self.start_recomp}
		self.wTree.signal_autoconnect(dic)
		
		##Here are some variables that can be reused later
		#self.cWine = 0
		#self.cWinery = 1
		#self.cGrape = 2
		#self.cYear = 3
		
		#self.sWine = "Wine"
		#self.sWinery = "Winery"
		#self.sGrape = "Grape"
		#self.sYear = "Year"		
				
		##Get the treeView from the widget Tree
		#self.wineView = self.wTree.get_widget("wineView")
		##Add all of the List Columns to the wineView
		#self.AddWineListColumn(self.sWine, self.cWine)
		#self.AddWineListColumn(self.sWinery, self.cWinery)
		#self.AddWineListColumn(self.sGrape, self.cGrape)
		#self.AddWineListColumn(self.sYear, self.cYear)
	
		##Create the listStore Model to use with the wineView
		#self.wineList = gtk.ListStore(str, str, str, str)
		##Attache the model to the treeView
		#self.wineView.set_model(self.wineList)	
		
	#def AddWineListColumn(self, title, columnId):
		#"""This function adds a column to the list view.
		#First it create the gtk.TreeViewColumn and then set
		#some needed properties"""
						
		#column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			#, text=columnId)
		#column.set_resizable(True)		
		#column.set_sort_column_id(columnId)
		#self.wineView.append_column(column)


		
	def OnAddWine(self, widget):
		print "add!!!!!!!!!"
		"""Called when the use wants to add a wine"""
		#Cteate the dialog, show it, and store the results
		wineDlg = wineDialog();		
		result,newWine = wineDlg.run()
		
		if (result == gtk.RESPONSE_OK):
			"""The user clicked Ok, so let's add this
			wine to the wine list"""
			self.wineList.append(newWine.getList())


	def onf(self, widget):
		dialog = gtk.FileChooserDialog("Open..",
                       None,
                       gtk.FILE_CHOOSER_ACTION_OPEN,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("Cue")
#		filter.add_mime_type("image/png")
#		filter.add_mime_type("image/jpeg")
#		filter.add_mime_type("image/gif")
		filter.add_pattern("*.cue")
#		filter.add_pattern("*.jpg")
#		filter.add_pattern("*.gif")
#		filter.add_pattern("*.tif")
#		filter.add_pattern("*.xpm")
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.entry = self.wTree.get_widget("entry1")
			self.entry.set_text(dialog.get_filename())
			pyWine.fileselect= dialog.get_filename()
		elif response == gtk.RESPONSE_CANCEL:
		   print "Closed, no files selected"	
		dialog.destroy()
#	def start_recomp(self, widget):		
#		MyThread1().setDaemon(True)
#		MyThread1().start()
		
	def start_recomp(self, widget):	
		combobox = self.wTree.get_widget("combobox1")
		codec=combobox.get_active_text()
		print codec
		#iter=combobox.set_active(0)
		#print iter
		pyWine.a=unicode('cue2tracks -c ' + codec + ' -Q7 -f cp1251 -R ' + '"' + pyWine.fileselect + '"')
		print pyWine.a
		
		textview = self.wTree.get_widget("textview1")
		pyWine.textbuffer=textview.get_buffer()
		pyWine.textbuffer.set_text('111111111')
#		print pyWine.a
#		mail = sys.stdin.read()
#		std=os.popen(pyWine.a)
#		ab = subprocess.Popen('grep', bufsize=1024, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
		pyWine.textbuffer.set_text("22222222")
#		p2 = threading.Thread(target=proc, name="t2", args=["2"]).setDaemon(True)
#		p2 = threading.Thread(target=proc, name="t2", args=["2"]).start()
#		MyThread1().setDaemon(True)
	#	MyThread1().run()
		gtk.threads_init()
		time.sleep(1)
		Test().start()
#		logcue = threading.Thread(target=log, name="log", args=["1"]).start()
#		print "start"
		time.sleep(3)
#		print "started"
#		if pyWine.proc1.isAlive():
#			print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
#		while 1:

		
#class wineDialog:
	#"""This class is used to show wineDlg"""
	
	#def __init__(self, wine="", winery="", grape="", year=""):
	
		##setup the glade file
		#self.gladefile = "pywine.glade"
		##setup the wine that we will return
		#self.wine = Wine(wine,winery,grape,year)
		
	#def run(self):
		#"""This function will show the wineDlg"""	
		
		##load the dialog from the glade file	  
		#self.wTree = gtk.glade.XML(self.gladefile, "wineDlg") 
		##Get the actual dialog widget
		#self.dlg = self.wTree.get_widget("wineDlg")
		##Get all of the Entry Widgets and set their text
		#self.enWine = self.wTree.get_widget("enWine")
		#self.enWine.set_text(self.wine.wine)
		#self.enWinery = self.wTree.get_widget("enWinery")
		#self.enWinery.set_text(self.wine.winery)
		#self.enGrape = self.wTree.get_widget("enGrape")
		#self.enGrape.set_text(self.wine.grape)
		#self.enYear = self.wTree.get_widget("enYear")
		#self.enYear.set_text(self.wine.year)	
	
		##run the dialog and store the response		
		#self.result = self.dlg.run()
		##get the value of the entry fields
		#self.wine.wine = self.enWine.get_text()
		#self.wine.winery = self.enWinery.get_text()
		#self.wine.grape = self.enGrape.get_text()
		#self.wine.year = self.enYear.get_text()
		
		##we are done with the dialog, destory it
		#self.dlg.destroy()
		
		##return the result and the wine
		#return self.result,self.wine
		

#class Wine:
	#"""This class represents all the wine information"""
	
	#def __init__(self, wine="", winery="", grape="", year=""):
		
		#self.wine = wine
		#self.winery = winery
		#self.grape = grape
		#self.year = year
		
	#def getList(self):
		#"""This function returns a list made up of the 
		#wine information.  It is used to add a wine to the 
		#wineList easily"""
		#return [self.wine, self.winery, self.grape, self.year]		


if __name__ == "__main__":
#	gtk.threads_init()
#	gobject.threads_init()
	wine = pyWine()
#	gtk.threads_enter()
	gtk.main()
#	gtk.threads_leave()

