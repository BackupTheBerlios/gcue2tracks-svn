#!/usr/bin/python
#-*- coding: utf8 -*-

import gtk
import gtk.glade
import threading
import popen2
from string import find
import time
import sys
import gettext
import locale
import pango
from config import *
from decoder import *
import getopt, gobject


VERSION = '0.4.2.1'

def treeview_setup_dnd(treeview):
	"""Setup a treeview to move rows using drag and drop.  """
	target_entries = [('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
						('text/plain', 0, 1),
						('TEXT', 0, 2),
						('STRING', 0, 3),]
	treeview.enable_model_drag_source(
		gtk.gdk.BUTTON1_MASK, target_entries, gtk.gdk.ACTION_MOVE)
	treeview.enable_model_drag_dest(target_entries, gtk.gdk.ACTION_MOVE)
	treeview.connect('drag-data-received', drag_data_received_data)
	treeview.connect('drag_data_get', drag_data_get_data)
	treeview.connect('cursor-changed', on_selection_changed)

def drag_data_get_data(treeview, context, selection, target_id, etime):
	treeselection = treeview.get_selection()
	model, iter = treeselection.get_selected()
	#self.data = map(lambda x:model.get_value(iter, x),[0,1,2,3])

def drag_data_received_data(treeview, context, x, y, selection, info, etime):
	model_to_copy, iter_to_copy = treeview.get_selection().get_selected()
	model = treeview.get_model()
	cursor_position = treeview.get_cursor()[0][0]
	Conversation.cursor = cursor_position,
	drop_info = treeview.get_dest_row_at_pos(x, y)
	if drop_info:
		path, position = drop_info
		iter = model.get_iter(path)
		if model.iter_depth(iter)is not 0:
			return
		if (position == gtk.TREE_VIEW_DROP_BEFORE
			or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
			model_to_copy.move_before(iter_to_copy, iter)
		else:
			model_to_copy.move_after(iter_to_copy, iter)
	else:
		model_to_copy.move_after(iter_to_copy, model.get_iter(len(model)-1))
	task_list_renew(model)

def on_selection_changed(treeview):
	cursor_position = treeview.get_cursor()[0]
	if not cursor_position:
		return
	task = Conversation.task_list[(cursor_position[0])]

	'''restore parametrs if cursor changes'''
	a = gui.bloc
	gui.bloc = True
	folder, dic = Conversation.task_parametrs[task]
	widget = [
		'quality', 'album', 'date', 'genre', 'composer'
		, 'bin_file', 'filename', 'performer']
	map(lambda x:glade.get_widget(x).set_text(dic[x]), widget)
	var = [
		'bitratebtn', 'VBR',
		'same_folder','qualitybtn']
	map(lambda x:glade.get_widget(x).set_active(dic[x]), var)
	glade.get_widget('level').set_active(dic['level_n'])
	glade.get_widget('codec').set_active(dic['codec_n'])
	glade.get_widget('bitrate').set_value(float(dic['bitrate']))
	glade.get_widget('savefolder').set_text(dic['folder'])
	gui.bloc = a

	if len(cursor_position) > 1:
		gui.renderer.set_property('editable', not get('cue2tracks'))
	else:
		gui.renderer.set_property('editable', False)
		if treeview.get_cursor()[1] is not treeview.get_column(3):
			if treeview.row_expanded(cursor_position):
				treeview.collapse_row(cursor_position)
			else:
				treeview.expand_to_path(cursor_position)


def notebook(widget,a,b):
	gobject.timeout_add(60, lambda: glade.get_widget('start').grab_focus())

def changeg (widget):
	glade.get_widget('VBR').set_sensitive(glade.get_widget('bitratebtn').get_active())
	glade.get_widget('bitrate').set_sensitive(glade.get_widget('bitratebtn').get_active())
	glade.get_widget('quality').set_sensitive(glade.get_widget('qualitybtn').get_active())
	codecn = glade.get_widget('codec').get_active_text()
	if codecn not in ['mp3','ogg']:
		glade.get_widget('VBR').set_sensitive(False)
		glade.get_widget('bitrate').set_sensitive(False)
		glade.get_widget('quality').set_sensitive(False)
		return
	if codecn == 'mp3' and get('mp3advance'):
		glade.get_widget('VBR').set_sensitive(True)
		glade.get_widget('bitrate').set_sensitive(True)
		glade.get_widget('quality').set_sensitive(True)
	if codecn == 'ogg':
		glade.get_widget('bitrate').set_range(32, 500)
	else:
		glade.get_widget('bitrate').set_range(32, 320)

def show_log (widget):
	show = glade.get_widget('show_log').get_active()
	glade.get_widget('log').set_property('visible', show)
	glade.get_widget('mainWindow').resize(1, 1)
	set('show_log', show)

def job_down (widget):
	cursor_position = gui.treeview.get_cursor()[0][0]
	if cursor_position == len(gui.tree_store) - 1:
		return
	iter = gui.tree_store.get_iter(cursor_position)
	gui.tree_store.move_after(iter, gui.tree_store.get_iter(cursor_position + 1))
	task_list_renew(gui.tree_store)

def job_up (widget):
	cursor_position = gui.treeview.get_cursor()[0][0]
	if cursor_position == 0:
		return
	iter = gui.tree_store.get_iter(cursor_position)
	gui.tree_store.move_before(iter, gui.tree_store.get_iter(cursor_position - 1))
	task_list_renew(gui.tree_store)

def task_list_renew(model):
	Conversation.task_list = []
	[Conversation.task_list.append(int(model[row][4]))
										 for row in range(len(model))]
	for n in range(len(Conversation.task_list)):
		model[n][0] = n + 1

class Searching_cue(threading.Thread):

	def run(self):
		self.bloc = True
		glade.get_widget('find_cue').set_sensitive(False)
		treeview = glade.get_widget('job queue')
		tree_store = treeview.get_model()
		folder_cue = glade.get_widget('find_cue_folder').get_text()
		set('find_cue_folder', folder_cue)
		if not os.path.isdir(folder_cue):
			return
		quality = glade.get_widget('quality').get_text ()
		bitrate = str(int(glade.get_widget('bitrate').get_value()))
		level = glade.get_widget('level').get_active_text()
		level_n = glade.get_widget('level').get_active()
		bitratebtn = glade.get_widget('bitratebtn').get_active()
		qualitybtn = glade.get_widget('qualitybtn').get_active()
		VBR = glade.get_widget('VBR').get_active()
		codec = glade.get_widget('codec').get_active_text()
		codec_n = glade.get_widget('codec').get_active()
		folder = glade.get_widget('savefolder').get_text()
		same_folder = glade.get_widget('same_folder').get_active()
		for root, dirs, files in os.walk(folder_cue):
			for name in files:
				if name.endswith('cue'):
					filename = os.path.join(root, name)
					GuiPart.folder = root
					if glade.get_widget('same_folder').get_active():
						folder = root
					'''get tag from cue file'''
					dic = {
		'performer': '', 'album': '', 'date': '', 'genre': '', 'composer': '',
		'bitrate': bitrate, 'quality': quality,	'filename': filename,
		'level': level, 'level_n': level_n,	'VBR': VBR,	'codec': codec,
		'bitratebtn': bitratebtn, 'qualitybtn': qualitybtn,
		'codec_n': codec_n, 'folder': folder, 'same_folder': same_folder,
					}
					f = open(filename, 'r')
					line = f.readline().replace('"','')
					gui.bin_filename = None
					while line:
						if 'TRACK' in line:
							break
						if 'GENRE' in line:
							dic['genre'] = line[10:-2]
						if 'DATE' in line:
							dic['date'] = line[9:-2]
						if 'PERFORMER' in line:
							dic['performer'] = gui.isutf(line)[10:-2]
						if 'COMPOSER' in line:
							dic['composer'] = gui.isutf(line)[9:-2]
						if 'TITLE' in line:
							dic['album'] = gui.isutf(line)[6:-2]
						if 'FILE' in line:
							gui.bin_filename = (gui.isutf(line)[5:-2]).replace(' WAVE','')
							full_path = os.path.join(root, gui.bin_filename)
							if not os.path.isfile(full_path.encode('utf-8')):
								gui.bin_filename = gui.find_bin(root)
								if not gui.bin_filename:
									gui.bin_filename = 'None'
									message = _('Bin file not found\n<b>%s</b>') %full_path
									gtk.gdk.threads_enter()
									print message.replace('<b>', '').replace('</b>', '')
									dialog = gtk.MessageDialog(parent=None,
											 flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_WARNING,
											  buttons=gtk.BUTTONS_OK)
									dialog.set_markup(message)
									gobject.timeout_add(10000, lambda: dialog.destroy())
									response = dialog.run()
									dialog.destroy()
									gtk.gdk.threads_leave()
							dic['bin_file'] = gui.bin_filename
						line = f.readline().replace('"','')
					if gui.bin_filename is None:
						f.close()
						break
					f.seek(0)
					track, filename ,title = [], [], []
					line = f.readline()
					while line:
						line = line.replace('"',"")
						if 'TITLE' in line and line[0]==' ':
							title.append(gui.isutf(line)[10:-2].strip())
						if 'TRACK' in line:
							track.append(line[8:10])
						if 'FILE' in line:
							filename.append(gui.isutf(line)[5:-2].replace(' WAVE',''))
						line = f.readline()
					f.close()
					'''get album light'''
					if len(filename) is not 1:
						dic['bin_files'] = filename
					Conversation.task_number += 1
					Conversation.task_list.append(Conversation.task_number)
					Conversation.task_parametrs[Conversation.task_number] = (
														GuiPart.folder, dic)
					gtk.gdk.threads_enter()
					tree_store.append(
								None, (len(Conversation.task_list), '%s - %s' % (dic['performer'], dic['album']), '',
								True, Conversation.task_number , None))
					treeview.set_cursor(len(tree_store) - 1)
					iter = tree_store.get_iter(len(tree_store) - 1)
					n = 0
					for item in title:
						n += 1
						tree_store.append(iter,
							(track[n-1], item, None, True, '',
							treeview.get_style().base[gtk.STATE_SELECTED].to_string()))
					gtk.gdk.threads_leave()
					break
		gtk.gdk.threads_enter()
		glade.get_widget('del_task').set_sensitive(True)
		if len(Conversation.task_list) == 2:
			glade.get_widget('job_up').set_sensitive(True)
			glade.get_widget('job_down').set_sensitive(True)

		if get('cue2tracks'):
			glade.get_widget('start').set_sensitive(True)
		glade.get_widget('start').set_sensitive(get('cue2tracks'))
		if len(Conversation.task_list) > 0 and not get('cue2tracks'):
			glade.get_widget('start').set_sensitive(True)
		glade.get_widget('test').set_sensitive(get('cue2tracks'))
		glade.get_widget('start').grab_focus()
		glade.get_widget('find_cue').set_sensitive(True)
		if len(Conversation.task_list) > 2:
			glade.get_widget('job_up').set_sensitive(True)
			glade.get_widget('job_down').set_sensitive(True)
		gtk.gdk.threads_leave()
		print 'searching cue done'
		self.bloc = False


class Add_queue(threading.Thread):

	def __init__(self, job_name):
		threading.Thread.__init__(self)
		self.job_name = job_name

	def run(self):

		def get_tags (tree_store):
			filename = glade.get_widget('filename').get_text()
			path = os.path.split(filename)[0]
			f = open(filename, 'r')
			track, filename ,title = [], [], []
			line = f.readline()
			while line:
				line = line.replace('"',"")
				if 'TITLE' in line and line[0]==' ':
					title.append(gui.isutf(line)[10:-2].strip())
				if 'TRACK' in line:
					track.append(line[8:10])
				if 'FILE' in line:
					filename.append(gui.isutf(line)[5:-2].replace(' WAVE',''))
				line = f.readline()
			f.close()
			'''get album light'''
			n = 0
			if len(filename) == 1:
				track_light1, light = track_light(
							path,glade.get_widget('bin_file').get_text(),glade)
				iter = tree_store.get_iter(len(tree_store)-1)
				gtk.gdk.threads_enter()
				for item in title:
					n += 1
					tree_store.append(iter,
						(track[n-1], item, track_light1[n-1], True, '',
						treeview.get_style().base[gtk.STATE_SELECTED].to_string()))
				tree_store[iter][2] = light
				gtk.gdk.threads_leave()
			else:
				iter = tree_store.get_iter(len(tree_store)-1)
				gtk.gdk.threads_enter()
				for item in title:
					n += 1
					tree_store.append(iter,
						(track[n-1], item, '', True, '',
						treeview.get_style().base[gtk.STATE_SELECTED].to_string()))
				glade.get_widget('bin_file').set_text('tracks')
				gtk.gdk.threads_leave()
				task = Conversation.task_list[-1]
				a = Conversation.task_parametrs[task][1]
				a.update(bin_files = filename)
				Conversation.task_parametrs[task] = (
						Conversation.task_parametrs[task][0], a)

		treeview = glade.get_widget('job queue')
		tree_store = treeview.get_model()
		gtk.gdk.threads_enter()
		tree_store.append(
					None, (len(Conversation.task_list), self.job_name, '',
					True, Conversation.task_number , None))
		treeview.set_cursor(len(tree_store) - 1)
		if len(threading.enumerate()) > 2:
			progressbar2=glade.get_widget('progressbar2')
			progressbar2.set_text(
					'%s   in queue:%s' %(Conversation.job_name
					, len(Conversation.task_list)))
		gtk.gdk.threads_leave()
		get_tags (tree_store)


class GuiPart:


	def __init__(self):

		def insert_one_tag_into_buffer(buffer, name, *params):
			tag = gtk.TextTag(name)
			while(params):
				tag.set_property(params[0], params[1])
				params = params[2:]
			table = buffer.get_tag_table()
			table.add(tag)

		self.bloc = True
		GuiPart.version = self.getver()
		dic = {'on_mainWindow_destroy' : self.endApplication
				,'onf' : self.onf, 'start_recomp' : self.start_recomp
				,'bsave' : self.bsave,'stop' : self.stop
				,'on_about1_activate' : self.on_about_activate
				,'test' : self.test,'codec_changed' : self.codec_changed
				,'changeg' : changeg,'sync' : self.sync
				,'show_log' : show_log,'note-book' : notebook
				,'on_preference_activate' : on_preference_activate
				,'add_task' : self.add_task, 'del_task' : self.del_task
				,'job_down' : job_down, 'job_up' : job_up,
				'find_cue' : self.find_cue, 'find_cue_dialog' : self.find_cue_dialog
				}
		glade.signal_autoconnect(dic)
		del dic
		bitrait = glade.get_widget('bitrate')
		'''read config'''
		bitrait.set_value(get('bitrait'))
		glade.get_widget('quality').set_text(get('quality'))
		glade.get_widget('savefolder').set_text(get('savepath'))
		glade.get_widget('find_cue_folder').set_text(get('find_cue_folder'))
		widget = [
			'same_folder', 'show_log', 'level', 'qualitybtn', 'VBR']
		map(lambda x:set(x,glade.get_widget(x).set_active(get(x))), widget)
		codecs_list(glade)
		if glade.get_widget('codec').get_active_text() == 'ogg':
			bitrait.set_range(32, 500)
		Conversation.task_number = 0
		Conversation.task_list = []
		Conversation.task_parametrs = {}
		GuiPart.textview = glade.get_widget('textview1')
		buffer=GuiPart.textview.get_buffer()
		insert_one_tag_into_buffer(buffer, 'bold', 'weight', pango.WEIGHT_BOLD)
		glade.get_widget('log').set_property('visible',get('show_log'))
		glade.get_widget('mainWindow').reshow_with_initial_size()
		'''first build'''
		self.treeview = glade.get_widget('job queue')
		self.treeview.set_rules_hint(True)
		self.tree_store = self.treeview.get_model()
		self.tree_store = gtk.TreeStore( str, str, str, 'gboolean', str, str)

		TARGETS = [
					('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
					('text/plain', 0, 1),
					('TEXT', 0, 2),
					('STRING', 0, 3),
					]

		self.treeview.set_model(self.tree_store)
		treeview_setup_dnd(self.treeview)
		renderer0 = gtk.CellRendererText()
		column = gtk.TreeViewColumn('', renderer0, text=0)
		self.renderer = gtk.CellRendererText()
		self.renderer.set_properties(
								xalign=0, editable=not get('cue2tracks'))
		self.renderer.connect('edited', col0_edited_cb, self.tree_store )
		self.renderer1 = gtk.CellRendererToggle()
		self.renderer1.set_properties(
							xalign=1.0, activatable=not get('cue2tracks'))
		self.renderer1.connect('toggled', col1_toggled_cb, self.tree_store )
		column1 = gtk.TreeViewColumn('', self.renderer1 )
		column1.add_attribute(self.renderer1, 'active', 3)
		column1.set_clickable(True)
		column2 = gtk.TreeViewColumn(_('Track light'), renderer0, text=2)
		column0 = gtk.TreeViewColumn(_('Track name'), self.renderer, text=1)
		column0.add_attribute(self.renderer, 'foreground', 5)
		column.add_attribute(renderer0, 'foreground', 5)
		column0.set_resizable(True)
		column1.set_resizable(False)
		self.treeview.append_column(column)
		self.treeview.append_column(column0)
		self.treeview.append_column(column2)
		self.treeview.append_column(column1)
		self.treeview.set_cursor(0)
		if ARGS:
			filename = ARGS[-1]
			if not os.path.isfile(filename):
				print _('Wrong filename'),filename
				sys.exit()
			path = os.path.split(filename)[0]
			glade.get_widget('filename').set_text(filename)
			glade.get_widget('start').set_sensitive(get('cue2tracks'))
			glade.get_widget('test').set_sensitive(get('cue2tracks'))
			self.bloc = True
			gtk.gdk.threads_enter()
			self.getcuetag(filename)
			gtk.gdk.threads_leave()
			self.add_task(self)
		self.bloc = False

	def on_about_activate(self,widget):
		"""
			about gcue2tracks
		"""
		Tree = gtk.glade.XML(pathglade, 'aboutdialog1', APP)
		about = Tree.get_widget('aboutdialog1')
		if  os.path.isfile('/usr/share/common-licenses/GPL-2'):
			fd = open('/usr/share/common-licenses/GPL-2')
			text = fd.read()
			about.set_license(text)
			fd.close()
		about.set_comments(
			'GTK+ Version: %s\nPyGTK Version: %s\ncue2tracks Version: %s'
			% (self.tuple2str(gtk.gtk_version),
			self.tuple2str(gtk.pygtk_version), GuiPart.version)
			)
		about.set_website('http://trac2.assembla.com/gCue2tracks/wiki/')
		about.set_version(VERSION)
		authors = []
		author = 'gCue2tracks: \n\tFomin Denis (fominde@gmail.com)\
		 \n\ncue2tracks:\n\tSergey (sergey.dryabzhinsky@gmail.com)'
		authors.append(author)
		authors.append(
		'\n%s\n\tOleg N. Stadnik (mail@lokee.rv.ua)\
		\n\tgoogle moogle' %_('THANKS:')
		)
		about.set_authors(authors)
		#about.set_artists('graf designer')
		for button in about.action_area.get_children():
			if button.get_property('label') == gtk.STOCK_CLOSE:
				button.connect('clicked', lambda x:about.destroy())
		about.run()

	def tuple2str(self, tuple_):
		str_ = ''
		for num in tuple_:
			str_ += str(num) + '.'
		return str_[0:-1]

	def getver(self):
		cue2tracks = '/usr/bin/cue2tracks'
		if os.path.isfile(cue2tracks):
			a=popen2.Popen4('cue2tracks -V')
			fromchild = a.fromchild.readline()
			return  fromchild
		return _('not installed')

	def codec_changed(self, widget):
		if glade.get_widget('codec').get_active_text() == 'mp3':
			is_bitratebtn = glade.get_widget('bitratebtn').get_active()
			glade.get_widget('VBR').set_sensitive(is_bitratebtn)
			glade.get_widget('bitrate').set_sensitive(is_bitratebtn)
			is_qualitybtn = glade.get_widget('qualitybtn').get_active()
			glade.get_widget('qualitybtn').set_active(is_qualitybtn)
			glade.get_widget('quality').set_sensitive(is_qualitybtn)
			glade.get_widget('bitrate').set_range(32, 320)
			glade.get_widget('level').set_sensitive(False)
			glade.get_widget('bitratebtn').set_sensitive(True)
			glade.get_widget('qualitybtn').set_sensitive(True)
			if get('mp3advance'):
				glade.get_widget('quality').set_sensitive(True)
			return
		if glade.get_widget('codec').get_active_text() == 'ogg':
			glade.get_widget('qualitybtn').set_active(get('qualitybtn'))
			glade.get_widget('VBR').set_sensitive(
				not glade.get_widget('qualitybtn').get_active())
			glade.get_widget('bitrate').set_sensitive(
				not glade.get_widget('qualitybtn').get_active())
			glade.get_widget('level').set_sensitive(False)
			glade.get_widget('bitrate').set_range(32, 500)
			glade.get_widget('bitratebtn').set_sensitive(True)
			glade.get_widget('qualitybtn').set_sensitive(True)
			glade.get_widget('quality').set_sensitive(
				glade.get_widget('qualitybtn').get_active())
			return
		widget = [
			'VBR', 'bitrate', 'quality', 'bitratebtn', 'qualitybtn']
		map(lambda x:glade.get_widget(x).set_sensitive(False), widget)
		glade.get_widget('level').set_sensitive(True)

	def sync(self, widget):
		if not self.bloc:
			cursor = self.treeview.get_cursor()
			if len(Conversation.task_list) < 1:
				cursor = ((0,0),0)
				Conversation.cursor = 0,
				return
			task = Conversation.task_list[(cursor[0][0])]
			a = Conversation.task_parametrs[task][1]
			a.update(parametrs(glade).items())
			Conversation.task_parametrs[task] = (
					Conversation.task_parametrs[task][0], a)

	def find_cue_dialog(self, widget):
		if get('cue2tracks'):
			return
		dialog = gtk.FileChooserDialog(_('Select folder'),None,
						gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		if not os.path.exists(get('open_folder')):
			set('open_folder', os.path.expanduser('~'))
		dialog.set_current_folder(get('open_folder'))
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			glade.get_widget('find_cue_folder').set_text(dialog.get_filename())
		dialog.destroy()

	def onf(self, widget):
		if get('cue2tracks'):
			gobject.timeout_add(60, lambda: clear_root_iter(glade))
		"""open file dialog"""
		dialog = gtk.FileChooserDialog(_('Open'),None,
						gtk.FILE_CHOOSER_ACTION_OPEN,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_OPEN, gtk.RESPONSE_OK))

		dialog.set_default_response(gtk.RESPONSE_OK)
		if not os.path.exists(get('open_folder')):
			set('open_folder', os.path.expanduser('~'))
		dialog.set_current_folder(get('open_folder'))
		filter = gtk.FileFilter()
		filter.set_name('Cue')
		filter.add_pattern('*.cue')
		dialog.add_filter(filter)
		filter = gtk.FileFilter()
		filter.set_name(_('All files'))
		filter.add_pattern('*')
		dialog.add_filter(filter)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.bloc = True
			self.filename = dialog.get_filename()
			glade.get_widget('filename').set_text(self.filename)
			GuiPart.folder = dialog.get_current_folder()
			if glade.get_widget('same_folder').get_active():
				glade.get_widget('savefolder').set_text(dialog.get_current_folder())
			glade.get_widget('test').set_sensitive(get('cue2tracks'))
			self.getcuetag()
			self.bloc = False
			if glade.get_widget('bin_file').get_text() is '':
				dialog.destroy()
				message = _('Bin file not found\n<b>%s</b>') %''
				show_dialog(message)
				return
			self.add_task(self)
			if get('cue2tracks'):
				glade.get_widget('start').set_sensitive(True)
			glade.get_widget('start').grab_focus()
		dialog.destroy()

	def getcuetag(self,filename = None):
		'''get tag from cue file'''
		if filename is None:
			if not os.path.isfile(self.filename):
				return
			path = os.path.split(self.filename)[0]
			f = open(self.filename, 'r')
		else:
			path = os.path.split(filename)[0]
			f = open(filename, 'r')
			if glade.get_widget('same_folder').get_active():
				glade.get_widget('savefolder').set_text(path)
			GuiPart.folder = path
		fields = ['genre', 'date', 'performer', 'album', 'composer']
		map(lambda x:glade.get_widget(x).set_text(''),fields)
		line = f.readline().replace('"','')
		while line:
			if 'TRACK' in line:
				break
			if 'GENRE' in line:
				glade.get_widget('genre').set_text(line[10:-2])
			if 'DATE' in line:
				glade.get_widget('date').set_text(line[9:-2])
			if 'PERFORMER' in line:
				glade.get_widget('performer').set_text(
				self.isutf(line)[10:-2])
			if 'COMPOSER' in line:
				glade.get_widget('composer').set_text(
				self.isutf(line)[9:-2])
			if 'TITLE' in line:
				glade.get_widget('album').set_text(
				self.isutf(line)[6:-2])
			if 'FILE' in line:
				a = (self.isutf(line)[5:-2]).replace(' WAVE','')
				full_path = os.path.join(path, a)
				if not os.path.isfile(full_path.encode('utf-8')):
					a = self.find_bin(path)
					if not a:
						a = 'None'
						message = _('Bin file not found\n<b>%s</b>') %full_path
						show_dialog(message)
				glade.get_widget('bin_file').set_text(a)
			line = f.readline().replace('"','')
		f.close()

	def find_cue(self, widget):
		thread = Searching_cue()
		thread.start()

	def find_bin(self,path):
		extention = ('ape','flac','wv','flake','wav')
		for ext in extention:
			if not os.path.isdir(path):
				return
			for name in os.listdir(path):
				path_name = os.path.join(path, name)
				if path_name.endswith(ext) or not ext:
					path_name = os.path.split(path_name)
					return path_name[-1].decode('utf8')

	def isutf(self, line):
		if get('convert_cue'):
			try:
				s = line.decode('utf-8')
			except:
				try:
					line = line.decode(get('codepage'))
				except :
					message = _('Bad codepage')
					print message
					dialog = gtk.MessageDialog(parent=None,
							 flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_WARNING,
							  buttons=gtk.BUTTONS_OK)
					dialog.set_markup(message)
					if len(threading.enumerate()) > 1:
						return ''
					response = dialog.run()
					dialog.destroy()
					line = '                              '
		return line

	def bsave(self, widget):

		def dialogdestroy(widget):
			dialog.destroy()

		def bsaveok(widget):
			path = dialog.get_filename().decode(sys.getfilesystemencoding())
			glade.get_widget('savefolder').set_text(path)
			set('save_folder', path)
			dialog.destroy()

		Tree = gtk.glade.XML(pathglade, 'filechooserdialog1',APP)
		dic = {'bsave_cancel' : dialogdestroy, 'bsave_ok' : bsaveok,}
		Tree.signal_autoconnect(dic)
		dialog = Tree.get_widget('filechooserdialog1')
		if not os.path.exists(get('open_folder')):
			set('save_folder', os.path.expanduser('~'))
		dialog.set_current_folder(get('save_folder'))
		response = dialog.run()

	def start_recomp(self, widget):
		self.testmode = 0
		self.start_recomp1(self)

	def test(self, widget):
		self.testmode = 1
		self.start_recomp1(self)

	def add_task(self, widget):
		Conversation.task_number += 1
		Conversation.task_list.append(Conversation.task_number)
		dic = parametrs(glade)
		if len(Conversation.task_list) == 2:
			glade.get_widget('job_up').set_sensitive(True)
			glade.get_widget('job_down').set_sensitive(True)
		Conversation.task_parametrs[Conversation.task_number] = (
											GuiPart.folder, dic)
		if len(threading.enumerate()) == 1:
			glade.get_widget('start').set_sensitive(not get('cue2tracks'))
		self.add_queue = Add_queue('%s - %s' % (dic['performer'], dic['album']))
		self.add_queue.start()
		glade.get_widget('del_task').set_sensitive(True)

	def del_task(self, widget):
		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()
		cursor_position = self.treeview.get_cursor()[0]
		if len(cursor_position) > 1:
			return
		if len(model) == 1:
			glade.get_widget('del_task').set_sensitive(False)
		cursor_position = self.treeview.get_cursor()[0][0]
		if Conversation.cursor[0] > cursor_position - 1:
			Conversation.cursor = Conversation.cursor[0]-1,
		if cursor_position +1 == len(model) and cursor_position != 0:
			self.treeview.set_cursor(cursor_position -1)
		if cursor_position +1 < len(model):
			self.treeview.set_cursor(cursor_position + 1)
		if iter:
			model.remove(iter)
			task_list_renew(model)
			if len(model) == 1:
				glade.get_widget('job_up').set_sensitive(False)
				glade.get_widget('job_down').set_sensitive(False)
		if len(Conversation.task_list) == 0:
			glade.get_widget('start').set_sensitive(False)
		if len(threading.enumerate()) > 1:
			progressbar2=glade.get_widget('progressbar2')
			progressbar2.set_text(
					'%s   in queue:%s' %(Conversation.job_name
					, len(Conversation.task_list)))


	def start_recomp1(self, widget):
		glade.get_widget('start').set_sensitive(False)
		glade.get_widget('test').set_sensitive(False)
		if not get('cue2tracks'):
			start_thread = Conversation(GuiPart.folder)
			start_thread.start()
			return
		glade.get_widget('stop_button').set_sensitive(True)
		dic = parametrs(glade)
		fileselect = ('"%s" ' %dic['filename']).decode('utf-8')
		folder = ' -o "%s' %dic['folder']
		self.codec = dic['codec']
		bin_file = ' -i "%s/%s"' % (GuiPart.folder, dic['bin_file'])
		test = ' -R '
		level = ' -l %s' %dic['level']
		codepage = disable_taging = self.bitrate = self.mode = self.quality = ''
		if self.codec in ['ogg','mp3']:
			self.getvar(dic)
		if get('convert_cue'):
			codepage = ' -f %s' %get('codepage')
		if get('disable_taging'):
			disable_taging = ' -d'
		if  self.testmode != 0:
			test = ''
		format = get('format') + '" '
		'''tagging'''
		album = ' -A "%s"' %dic['album']
		performer = ' -P "%s"' %dic['performer']
		date = ' -D "%s"' %dic['date']
		genre = ' -G "%s"' %dic['genre']
		composer = ' -K "%s"' %dic['composer']
		GuiPart.a1=unicode('cue2tracks -n 15 -c ' + self.codec
		+ bin_file.decode('utf-8') + disable_taging
		+ album + performer + composer + date + genre +level
		+ self.bitrate + self.mode + self.quality
		+ codepage + test + folder + format + fileselect)
		print GuiPart.a1.encode('utf-8')
		self.goButton_clicked(widget)

	def getvar(self, dic):
		if dic['bitratebtn']:
			if dic['VBR']:
				self.mode = ' -M -V'
			else:
				self.mode = ' -M -C'
			self.bitrate = ' -B %s' % dic['bitrate']
			self.quality = ''
		else:
			self.quality = ' -Q %s' % dic['quality']
			self.bitrate = self.mode = ''
		if self.codec == 'mp3' and get('mp3advance'):
			if dic['VBR']:
				self.mode = ' -M -V'
			else:
				self.mode = ' -M -C'
			self.bitrate = ' -B %s' % dic['bitrate']
			self.quality = ' -Q %s' % dic['quality']

	def goButton_clicked(self,widget):
		glade.get_widget('start').set_sensitive(False)
		glade.get_widget('test').set_sensitive(False)
		self.s = Convert()
		self.s.start()

	def quitButton_clicked(self,widget):
		self.endApplication()

	def stop(self,widget):
		glade.get_widget('stop_button').set_sensitive(False)
		if len(Conversation.task_list) > 0:
			glade.get_widget('start').set_sensitive(True)
		if get('cue2tracks'):
			glade.get_widget('start').set_sensitive(True)
			glade.get_widget('test').set_sensitive(True)
			self.s.a=0
			popen2.Popen3('killall -Iq cue2tracks')
			glade.get_widget('progressbar1').set_fraction (0.0)
			glade.get_widget('progressbar1').set_text (_('Interrupted'))
			return
		treads = threading.enumerate()
		a = treads[1].stop()
		Conversation.value = (_('Interrupted'))
		if a:
			try:
				os.kill(a, 9)
			except:
				pass

	def endApplication(self,widget):
		popen2.Popen4('killall -q cue2tracks')
		if len(threading.enumerate()) > 1:
			self.stop(None)
			clean_tmp(get('tmpdir'))
		widget = [
			'same_folder', 'codec', 'level', 'bitratebtn', 'qualitybtn', 'VBR']
		map(lambda x:set(x,glade.get_widget(x).get_active()), widget)
		set('savepath',glade.get_widget('savefolder').get_text())
		set('quality',glade.get_widget('quality').get_text())
		set('bitrait',glade.get_widget('bitrate').get_value())
		write()
		gtk.main_quit()


class Convert(threading.Thread):

	def run(self):
		#print os.getpid()
		set_text_progressbar1('')
		GuiPart.textview = glade.get_widget('textview1')
		buffer = GuiPart.textview.get_buffer()
		buffer.delete(buffer.get_start_iter(),buffer.get_end_iter())
		try:
			self.a = 1
			Thread = threading.Thread(target = self.puls_progressbar)
			Thread.start()
			command = (GuiPart.a1).encode('utf-8')
			proc1 = popen2.Popen4(command)
			self.print_log(proc1,buffer,command)
			if gui.codec == 'mp3' and get('mp3_utf') and gui.testmode == 0:
				'''python-mutagen'''
				ext = 'mp3'
				folder = glade.get_widget('savefolder')\
				.get_text().decode(sys.getfilesystemencoding())
				for root,dirs,files in os.walk(folder):
					for f in files:
						if f.endswith(ext) or not ext:
							conv = 'mid3iconv -e UTF-8 "%s/%s"' % (root, f)
							proc1 = popen2.Popen4(conv.encode('utf-8'))
							command = ''
							self.print_log(proc1,buffer,command)
			self.a=0
			glade.get_widget('start').set_sensitive(True)
			glade.get_widget('test').set_sensitive(True)
			glade.get_widget('stop_button').set_sensitive(False)
			progressbar = glade.get_widget('progressbar1')
			if proc1.poll() not in [256,0,-1]:
				gtk.gdk.threads_enter()
				progressbar.set_fraction (0.0)
				progressbar.set_text (_('Error'))
				gtk.gdk.threads_leave()
			elif proc1.poll() == 0:
				gtk.gdk.threads_enter()
				progressbar.set_fraction (1)
				progressbar.set_text (_('Complete'))
				gtk.gdk.threads_leave()
		except:
			pass

	def print_log(self,proc1,buffer,command):
		gtk.gdk.threads_enter()
		buffer.insert(buffer.get_end_iter(), command + '\n')
		gtk.gdk.threads_leave()
		while proc1.poll() == -1:
			fromchild = proc1.fromchild.readline()
			a1 = find(fromchild,'%')
			if a1 != -1:
				fromchild = fromchild[:(a1-4)]
			print fromchild
			gtk.gdk.threads_enter()
			buffer.insert(buffer.get_end_iter(), fromchild)
			index = find(fromchild,'Track')
			index1 = find(fromchild,':')
			if index != -1 and index1 != -1:
				if find(fromchild,'\n') == -1:
					buffer.insert(buffer.get_end_iter(), '\n')
				a = buffer.get_line_count()
				buffer.apply_tag_by_name(
				'bold',buffer.get_iter_at_line_offset(a-2,index),\
				 buffer.get_iter_at_line_offset(a-2,index1))
			match_start_mark = buffer.create_mark(
				'match_start', buffer.get_end_iter(), True)
			GuiPart.textview.scroll_to_mark(match_start_mark, 0, True)
			gtk.gdk.threads_leave()

	def puls_progressbar(self):
		a2=glade.get_widget('progressbar1')
		while self.a==1:
			gtk.gdk.threads_enter()
			a2.pulse()
			gtk.gdk.threads_leave()
			time.sleep (0.015)


gtk.gdk.threads_init()
APP = 'gCue2tracks'
DIR = '/usr/share/locale'
locale.setlocale(locale.LC_ALL, '')

for module in (gettext, gtk.glade):
	module.bindtextdomain(APP, DIR)
	module.textdomain(APP)

#gettext.install(APP, DIR, unicode = True)
_ = gettext.gettext

if os.path.dirname(sys.argv[0]) != '/usr/bin':
	workdir = os.getcwd()
else:
	workdir = '/usr/share/gcue2tracks'

pathglade = os.path.join(workdir, 'gCue2tracks.glade')
glade = gtk.glade.XML(pathglade, 'mainWindow', APP)
QUIET = None

longargs = 'help quiet output'
try:
	opts, args = getopt.getopt(sys.argv[1:], 'hqo:', longargs.split())
	ARGS = args
except getopt.GetoptError, err:
		print str(err)
		sys.exit(2)

for o, a in opts:
	if o in ('-h', '--help'):
		print 'gCue2tracks [--help] [--quiet] inputfile [...]'
		sys.exit()
	if o in ('-q', '--quiet'):
		print 'will be done later :-)'
		QUIET = True
	if o in ('-o', '--output'):
		print a

Conversation.cursor = [0]
gui = GuiPart()
varc(glade, pathglade, QUIET)
gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()

