#!/usr/bin/python
#

import gtk
import gtk.glade   
import threading
import popen2
import string

def puls1():
	a=GuiPart.wTree.get_widget("progressbar1")	
	if ThreadedClient.a==1:
		gtk.gdk.threads_enter()
		a.pulse()
		gtk.gdk.threads_leave()
		a=threading.Timer(0.02, puls).start()
		
def puls():
	puls1()

def bitratebtn (widget):
	GuiPart.wTree.get_widget("VBR").set_sensitive(True)
	GuiPart.wTree.get_widget("bitrate").set_sensitive(True)
	GuiPart.wTree.get_widget("quality").set_sensitive(False)
	
def qualitybtn (widget):
	GuiPart.wTree.get_widget("VBR").set_sensitive(False)	
	GuiPart.wTree.get_widget("bitrate").set_sensitive(False)
	GuiPart.wTree.get_widget("quality").set_sensitive(True)

class GuiPart:
	def __init__(self):
		gladefile = "gCue2tracks.glade"  
		GuiPart.wTree = gtk.glade.XML(gladefile, "mainWindow") 
		combobox = GuiPart.wTree.get_widget("codec")
		iter=combobox.set_active(0)
		self.R=[1]	
		dic = {"on_mainWindow_destroy" : self.endApplication
				, "onf" : self.onf, "start_recomp" : self.start_recomp
				,"bsave" : self.bsave,"stop" : self.stop,"codec_changed" : self.codec_changed
				,"bitratebtn" : bitratebtn,"qualitybtn" : qualitybtn
				,"on_about1_activate" : self.on_about_activate,"test" : self.test}
		GuiPart.wTree.signal_autoconnect(dic)
		bitrait = GuiPart.wTree.get_widget("bitrate")
		store = gtk.ListStore(str)
		store.append (["128"])
		store.append (["196"])
		store.append (["256"])
		store.append (["320"])
		bitrait.set_model(store)
		bitrait.set_text_column(0)
		bitrait.set_active(0)

	def on_about_activate(self,widget):
		Tree = gtk.glade.XML("gCue2tracks.glade", "aboutdialog1")
		about = Tree.get_widget("aboutdialog1")
		text = open('COPYING').read()
		about.set_license(text)
		about.set_comments(  'GTK+ Version: ' + self.tuple2str(gtk.gtk_version)
		 + '\n' + 'PyGTK Version: ' + self.tuple2str(gtk.pygtk_version))
		for button in about.action_area.get_children():
			if button.get_property('label') == gtk.STOCK_CLOSE:
				button.connect('clicked', lambda x:about.destroy())
		about.run()

	def tuple2str(self, tuple_):
		str_ = ''
		for num in tuple_:
			str_ += str(num) + '.'
		return str_[0:-1]
			 
	def codec_changed(self, widget):
		codecn = GuiPart.wTree.get_widget("codec").get_active()
		if codecn in [0,1]:
			GuiPart.wTree.get_widget("hbox1").set_sensitive(True)
			GuiPart.wTree.get_widget("hbox2").set_sensitive(True)
			bitratebtn (widget)
			GuiPart.wTree.get_widget("bitratebtn").set_active(True)
		else :
			GuiPart.wTree.get_widget("hbox1").set_sensitive(False)
			GuiPart.wTree.get_widget("hbox2").set_sensitive(False)

	def onf(self, widget):
		dialog = gtk.FileChooserDialog("Open",
						None,
						gtk.FILE_CHOOSER_ACTION_OPEN,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("Cue")
		filter.add_pattern("*.cue")
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			GuiPart.wTree.get_widget("filename").set_text(dialog.get_filename())
			if GuiPart.wTree.get_widget("savefolder").get_text()=='':
				GuiPart.wTree.get_widget("savefolder").set_text(dialog.get_current_folder())
			GuiPart.wTree.get_widget("start").set_sensitive(True)
			GuiPart.wTree.get_widget("test").set_sensitive(True)
		elif response == gtk.RESPONSE_CANCEL:
		   print "Closed, no files selected"	
		dialog.destroy()

	def bsave(self, widget):
		def dialogdestroy(widget):
			dialog.destroy()
		def bsaveok(widget):
			GuiPart.wTree.get_widget("savefolder").set_text(dialog.get_filename())
			dialog.destroy()
		Tree = gtk.glade.XML("gCue2tracks.glade", "filechooserdialog1")
		dic = {"bsave_cancel" : dialogdestroy, "bsave_ok" : bsaveok,}
		Tree.signal_autoconnect(dic) 
		dialog = Tree.get_widget("filechooserdialog1")
		response = dialog.run()

	def start_recomp(self, widget):
		self.start_recomp1(self,testmode=0)
		
	def test(self, widget):
		self.start_recomp1(self,testmode=1)

	def start_recomp1(self, widget,testmode):
		GuiPart.wTree.get_widget("stop_button").set_sensitive(True)
		fileselect= ' "' + GuiPart.wTree.get_widget("filename").get_text() + '"'  ## filename
		folder = ' -o "' + GuiPart.wTree.get_widget("savefolder").get_text()      ## folder to save
		level = ' -l fast'
		codepage =disable_taging =''
		self.bitrate = self.mode = self.quality = ''
		if GuiPart.wTree.get_widget("best").get_active():
			level = ' -l best'
		codec = GuiPart.wTree.get_widget("codec").get_active_text()
		if codec in ['ogg','mp3']:
			self.getvar()
		if GuiPart.wTree.get_widget("convert_cue").get_active():
			codepage = ' -f ' + GuiPart.wTree.get_widget("codepage").get_text ()
		if GuiPart.wTree.get_widget("disable_taging").get_active():
			disable_taging = ' -d'
		test = ' -R '
		if  testmode<>0:
			test = ''
		format = GuiPart.wTree.get_widget("format").get_text ()+ '"'
		GuiPart.a=unicode('cue2tracks -c ' + codec + disable_taging + level + self.bitrate + self.mode + self.quality 
							+ codepage + test + folder + format + fileselect)
		print GuiPart.a ######################
		self.goButton_clicked(widget)

	def getvar(self):
		if GuiPart.wTree.get_widget("bitratebtn").get_active():
			if GuiPart.wTree.get_widget("VBR").get_active():
				self.mode = " -M -V"
			else:
				self.mode = " -M -C"
			self.bitrate =" -B " + GuiPart.wTree.get_widget("bitrate").child.get_text()
			self.quality =''
		else:
			self.quality = ' -Q' + GuiPart.wTree.get_widget("quality").get_text ()
			self.bitrate =self.mode =''

	def goButton_clicked(self,widget):
		GuiPart.wTree.get_widget("start").set_sensitive(False)
		GuiPart.wTree.get_widget("test").set_sensitive(False)
		self.incomingThread=threading.Thread(target=self.Incoming)
		self.incomingThread.setDaemon(True)
		self.incomingThread.start()		

	def quitButton_clicked(self,widget):
		self.endApplication()

	def stop(self,widget):
		GuiPart.wTree.get_widget("stop_button").set_sensitive(False)
		GuiPart.wTree.get_widget("start").set_sensitive(True)
		GuiPart.wTree.get_widget("test").set_sensitive(True)
		ThreadedClient.a=0
		popen2.Popen3('killall -Iq cue2tracks')
		GuiPart.wTree.get_widget("progressbar1").set_fraction (0.0)
		GuiPart.wTree.get_widget("progressbar1").set_text ('Interrupted')
		return

	def endApplication(self,widget):
		popen2.Popen4('killall -q cue2tracks')
		print "time to die"
		gtk.main_quit()

	def Incoming(self):
		GuiPart.wTree.get_widget("progressbar1").set_text ('')
		GuiPart.textview = GuiPart.wTree.get_widget("textview1")
		GuiPart.textbuffer=GuiPart.textview.get_buffer()
		try:
			ThreadedClient.a=1
			threading.Thread(target=puls).start()
			proc1 = popen2.Popen4(GuiPart.a)
			while proc1.poll()==-1:
				
				fromchild = proc1.fromchild.readline()
				a=string.find(fromchild,'%')
				if a<>-1:
					fromchild = fromchild[:(a-3)]
				print fromchild
				gtk.gdk.threads_enter()
				buff=GuiPart.textbuffer.get_text(GuiPart.textbuffer.get_start_iter(),\
				GuiPart.textbuffer.get_end_iter())                  	   
				GuiPart.textbuffer.set_text( buff+fromchild+ '\n')
				match_start_mark = GuiPart.textbuffer.create_mark('match_start',\
				GuiPart.textbuffer.get_end_iter(), True)
				GuiPart.textview.scroll_to_mark(match_start_mark, 0, True)
				#if proc1.poll() not in [256,0,-1]:
					#print 'ERRRRRor' , proc1.poll()
					#GuiPart.wTree.get_widget("progressbar1").set_fraction (0.1)
				gtk.gdk.threads_leave()
			ThreadedClient.a=0
			GuiPart.wTree.get_widget("start").set_sensitive(True)
			GuiPart.wTree.get_widget("test").set_sensitive(True)
			GuiPart.wTree.get_widget("stop_button").set_sensitive(False)
			if proc1.poll() not in [256,0,-1]:
				gtk.gdk.threads_enter()
				GuiPart.wTree.get_widget("progressbar1").set_fraction (0.0)
				GuiPart.wTree.get_widget("progressbar1").set_text ('Error')
				gtk.gdk.threads_leave()
			elif proc1.poll()==0:
				gtk.gdk.threads_enter()
				GuiPart.wTree.get_widget("progressbar1").set_fraction (1)
				GuiPart.wTree.get_widget("progressbar1").set_text ('Complete')
				gtk.gdk.threads_leave()
		except :
			pass  


class ThreadedClient:
	def __init__(self):
		gtk.gdk.threads_init()
		self.gui=GuiPart()
		gtk.main()

plop=ThreadedClient()

#  if not widget.props.sensitive:
#    print "I'm insensitive!"
#                print proc1.pid
	#-A <album> : Set album title.
	#-P <performer> : Set album performer.
	#-D <date> : Set album date.
	#-G <genre> : Set album genre.
	#-o <format string> : Set naming scheme for output files.
	#Naming scheme is:
		#%A : Album title
		#%P : Album performer
		#%D : Album date
		#%G : Album genre
		#%t : Track title
		#%p : Track performer
		#%g : Track genre
		#%n : Track number
		#%N : Track number with leading zero
	#-V : Print version and exit.
	#-h : Print this help and exit.
	#-q : Quite mode - only errors to stderr.
	#-s : Start spliting even in testing mode (to /dev/null).
	#-n <level> : nice level of codecs (process scheduling priority): -19 to 19.
	#-R : Disable testing and doing nothing - starts Real work.

	#Options only for mp3, ogg:
	#-Q <quality> : Set quality of codec compression (4 - default).
	#Quality may be:
		#MP3: 0 - high, 9 - low
		#OGG: -1 - low, 10 - high
	#-B <bitrate> : Set compression bitrate in kbps (128 default).
	#-M <bitrate mode> : C - Constant, V - Variable (default).
		#If choosen V - then -B specifies maximum bitrate.

#To get some action:
	#cue2tracks -c flac -f cp1251 -o "/path/to/music/%P/%D - %A/%N" CDimage.cue
