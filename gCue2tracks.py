#!/usr/bin/python
#

import gtk
import gtk.glade   
import threading
import Queue
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
		
class aJob:

	def __init__(self,id,label):
		self.id=id
		self.label=label
		self.result=None
		
class GuiPart:
	def __init__(self,qIn,qOut):
		self.qIn=qIn
		self.qOut=qOut
		self.jobCounter=0
		self.currentJobId=None
		gladefile = "gCue2tracks.glade"  
		GuiPart.wTree = gtk.glade.XML(gladefile, "mainWindow") 
		combobox = GuiPart.wTree.get_widget("codec")
		iter=combobox.set_active(0)	
		dic = {"on_mainWindow_destroy" : self.endApplication
				, "onf" : self.onf, "start_recomp" : self.start_recomp
				,"bsave" : self.bsave,"stop" : self.stop,"codec_changed" : self.codec_changed
				,"bitratebtn" : bitratebtn,"qualitybtn" : qualitybtn}
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
		
	def codec_changed(self, widget):
		codecn1 = GuiPart.wTree.get_widget("codec")
		codecn=codecn1.get_active()
		if codecn<=1:
			GuiPart.wTree.get_widget("hbox1").set_sensitive(True)
			GuiPart.wTree.get_widget("hbox2").set_sensitive(True)
			bitratebtn (widget)
			GuiPart.wTree.get_widget("bitratebtn").set_active(True)
		else :
			GuiPart.wTree.get_widget("hbox1").set_sensitive(False)
			GuiPart.wTree.get_widget("hbox2").set_sensitive(False)

	def onf(self, widget):
		dialog = gtk.FileChooserDialog("Open..",
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
		fileselect= ' "' + GuiPart.wTree.get_widget("filename").get_text() + '"'  ## filename
		folder = ' -o "' + GuiPart.wTree.get_widget("savefolder").get_text()      ## folder to save
		codec = GuiPart.wTree.get_widget("codec").get_active_text()
		if GuiPart.wTree.get_widget("VBR").get_active():
			mode = " -M -V"
		else:
			mode = " -M -C"
		bitrate =" -B " + GuiPart.wTree.get_widget("bitrate").child.get_text()
		quality = ' -Q' + GuiPart.wTree.get_widget("quality").get_text ()
		codepage = ' -f cp1251'
		test = ' -R'
		GuiPart.a=unicode('cue2tracks -c ' + codec + bitrate + mode + quality 
							+ codepage + test + folder + '/%P/%D - %A/%t"'+ fileselect)
		print GuiPart.a ######################
		self.goButton_clicked(widget)

	def goButton_clicked(self,widget):
		id=self.jobCounter
		self.jobCounter+=1
		job=aJob(id,'11')
		self.qIn.put(job)
		
	def stop(self,widget):
		popen2.Popen4('killall cue2tracks')

	def quitButton_clicked(self,widget):
		self.endApplication()

	def endApplication(self,widget):
		popen2.Popen4('killall cue2tracks')
		print "time to die"
		gtk.main_quit()

class ThreadedClient:
    def __init__(self):
        gtk.gdk.threads_init()
        self.qIn=Queue.Queue()
        self.qOut=Queue.Queue()
        self.gui=GuiPart(self.qIn,self.qOut)
        self.running=True
        self.incomingThread=threading.Thread(target=self.processIncoming)
        self.incomingThread.setDaemon(True)
        self.incomingThread.start()
        gtk.main()
        self.running=False
        
    def processIncoming(self):
        GuiPart.textview = GuiPart.wTree.get_widget("textview1")
        GuiPart.textbuffer=GuiPart.textview.get_buffer()
        while self.running:
                while self.qIn.qsize():
                    try:
                        job=self.qIn.get(0)
                        ThreadedClient.a=1
                        self.gui.currentJobId=job.id
                        threading.Thread(target=puls).start()
                        proc1 = popen2.Popen4(GuiPart.a)
                        gtk.gdk.threads_enter()
                        fromchild = proc1.fromchild.readline()
                        gtk.gdk.threads_leave()
                        while fromchild:
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
                            gtk.gdk.threads_leave()	
                        job.result=' '
                        ThreadedClient.a=2
                        self.gui.currentJobId=None
                        self.qOut.put(job)
                    except Queue.Empty:
                       pass  
    
    #def endApplication(self):
        #self.running=False

plop=ThreadedClient()


#  if not widget.props.sensitive:
#    print "I'm insensitive!"
