#!/usr/bin/python
#-*- coding: utf8 -*-

import gettext
import threading
import gtk
import gtk.glade
import popen2
import os
import sys
import gtk
import tempfile
import string
import shutil
from config import *
import gobject
import re

_ = gettext.gettext

def on_preference_activate(widget):

	def notebook(widget,a,b):
		gobject.timeout_add(10, lambda: Tree.get_widget('close').grab_focus())

	def bsavep(widget):

		def dialogdestroy(widget):
			dialog.destroy()

		def bsaveok(widget):
			path = dialog.get_filename()
			if button == 'savefolder_preference_btn':
				Tree.get_widget('open_folder').set_text(path)
				set('open_folder', path)
			else:
				Tree.get_widget('tmp_dir').set_text(path)
				set('tmp_dir', path)
			dialog.destroy()

		button = widget.get_name()
		glade = gtk.glade.XML(pathglade, 'filechooserdialog1', 'gCue2tracks')
		dic = {'bsave_cancel' : dialogdestroy, 'bsave_ok' : bsaveok}
		glade.signal_autoconnect(dic)
		dialog = glade.get_widget('filechooserdialog1')
		dialog.set_current_folder(os.path.expanduser('~'))
		response = dialog.run()

	def codec_btn(widget):
		def dialogdestroy(widget):
			dialog.destroy()
		def bsaveok(widget):
			path = dialog.get_filename()
			Tree.get_widget(button[:-3]).set_text(path)
			set('widget', path)
			dialog.destroy()
		button = widget.get_name()
		glade = gtk.glade.XML(pathglade, 'filechooserdialog1', 'gCue2tracks')
		dic = {'bsave_cancel' : dialogdestroy, 'bsave_ok' : bsaveok}
		glade.signal_autoconnect(dic)
		dialog = glade.get_widget('filechooserdialog1')
		dialog.set_current_folder(os.path.expanduser('~'))
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
		dialog.set_title('Open')
		response = dialog.run()

	def destroy(widget):
		map(lambda x: set(x, Tree.get_widget(x).get_text()), widgets)
		widgets_ = [
			'cue2tracks', 'filename_filter', 'mp3advance', 'mp3_utf',
			'disable_taging', 'convert_cue', 'copy_image']
		map(lambda x:set(x, Tree.get_widget(x).get_active()), widgets_)
		window.destroy()

	def cue2tracks(widget):
		is_cue2tracks = Tree.get_widget('cue2tracks').get_active()
		set('cue2tracks', is_cue2tracks)
		codecs_list(glade)
		if glade.get_widget('filename').get_text():
			glade.get_widget('test').set_sensitive(is_cue2tracks)
			glade.get_widget('start').set_sensitive(is_cue2tracks)
			glade.get_widget('del_task').set_sensitive(not is_cue2tracks)

	def mp3_utf (widget):
		if not os.path.isfile('/usr/bin/mid3v2') and Tree.get_widget('mp3_utf').get_active():
			Tree.get_widget('mp3_utf').set_active(False)
			message = _('mid3v2 (from python-mutagen) is not found')
			show_dialog(message)

	global Tree
	Tree = gtk.glade.XML(pathglade, 'preferences_window', 'gCue2tracks')
	dic = {
		'destroy' : destroy, 'bsavep' : bsavep, 'cue2tracks' : cue2tracks,
		'tmp_dir' : bsavep, 'notebook' : notebook, 'codec_btn' : codec_btn,
		'mp3_utf' : mp3_utf
			}
	Tree.signal_autoconnect(dic)

	'''restore dialog state'''
	widgets_ = [
			'cue2tracks', 'filename_filter', 'mp3advance', 'mp3_utf',
			'disable_taging', 'convert_cue', 'copy_image']
	map(lambda x:Tree.get_widget(x).set_active(get(x)), widgets_)

	widgets = [
		'tmp_dir', 'format', 'ogg', 'mp3', 'flac', 'mac',
		'wavpack', 'wvunpack', 'open_folder', 'codepage']
	map(lambda x:Tree.get_widget(x).set_text(get(x)), widgets)
	window = Tree.get_widget('preferences_window')
	window.show()

def codecs_list(glade):
	if get('cue2tracks'):
		codecs = ['ogg', 'mp3', 'flac', 'wav', 'flake', 'ape', 'wv', 'ofr', 'shn']
	else:
		codecs = ['ogg', 'mp3', 'flac', 'wav', 'ape', 'wv']
	list = glade.get_widget('codec').get_model()
	list.clear()
	map(lambda x:list.append([x]), codecs)
	st = get('codec')
	glade.get_widget('codec').set_active(st)

def varc(glade1, pathglade1, QUIET):
	global glade, pathglade, QUIET1
	glade = glade1
	pathglade = pathglade1
	QUIET1 = QUIET

def parametrs(glade):
	dic = {
		'performer': glade.get_widget('performer').get_text(),
		'bitrate': str(int(glade.get_widget('bitrate').get_value())),
		'quality': glade.get_widget('quality').get_text (),
		'album': glade.get_widget('album').get_text(),
		'date': glade.get_widget('date').get_text(),
		'genre': glade.get_widget('genre').get_text(),
		'composer': glade.get_widget('composer').get_text(),
		'level': glade.get_widget('level').get_active_text(),
		'level_n': glade.get_widget('level').get_active(),
		'bitratebtn': glade.get_widget('bitratebtn').get_active(),
		'qualitybtn': glade.get_widget('qualitybtn').get_active(),
		'VBR': glade.get_widget('VBR').get_active(),
		'bin_file': glade.get_widget('bin_file').get_text(),
		'filename': glade.get_widget('filename').get_text(),
		'codec': glade.get_widget('codec').get_active_text(),
		'codec_n': glade.get_widget('codec').get_active(),
		'folder': glade.get_widget('savefolder').get_text(),
		'same_folder': glade.get_widget('same_folder').get_active(),
		}
	return dic

def show_dialog(message):
	print message.replace('<b>', '').replace('</b>', '')
	dialog = gtk.MessageDialog(parent=None,
			 flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_WARNING,
			  buttons=gtk.BUTTONS_OK)
	dialog.set_markup(message)
	gobject.timeout_add(10000, lambda: dialog.destroy())
	response = dialog.run()
	if not os.path.exists(get('tmpdir')):
		dialog.destroy()
		return
	clean_tmp(get('tmpdir'))
	dialog.destroy()

def set_text_progressbar1(text):
	gtk.gdk.threads_enter()
	glade.get_widget('progressbar1').set_text(text)
	gtk.gdk.threads_leave()

def	set_fraction_progressbar1(fraction):
	gtk.gdk.threads_enter()
	glade.get_widget('progressbar1').set_fraction(fraction)
	gtk.gdk.threads_leave()

def start(parametrs):

	def get_command(name='wav.wav'):
		dec_command = {
					'ape':'%s "%s" "%s/wav.wav" -d' % (get('mac'), bin_file, tmpdir),
					'flac':'%s -d -f -o "%s/%s" "%s"' % (get('flac'), tmpdir, name, bin_file),
					'wv':'%s -o "%s/wav.wav" "%s"' % (get('wvunpack'), tmpdir, bin_file),
					'wav':'cp "%s" "%s/wav.wav"' % (bin_file, tmpdir)
					}
		gtk.gdk.threads_enter()
		glade.get_widget('stop_button').set_sensitive(True)
		glade.get_widget('start').set_sensitive(False)
		glade.get_widget('test').set_sensitive(False)
		gtk.gdk.threads_leave()
		codec = bin_file.split('.')[-1]
		if codec in dec_command:
			'''codec supported?'''
			command = dec_command[codec]
		else:
			gtk.gdk.threads_enter()
			message = _('Format <b>%s</b>\ndon\'t supported '
								) %codec
			show_dialog(message)
			glade.get_widget('stop_button').set_sensitive(False)
			glade.get_widget('start').set_sensitive(True)
			gtk.gdk.threads_leave()
			return

		if codec == 'wv' and not codec_path('wvunpack'):
				return
		if codec == 'ape'and not codec_path('mac'):
				return
		if codec == 'flac'and not codec_path('flac'):
				return
		return command

	def find_bin(path, fname):
		extention = ('ape','flac','wv','flake','wav')
		fname = fname.split('.')[-2]
		for ext in extention:
			if not os.path.isdir(path):
				return
			for name in os.listdir(path):
				path_name = os.path.join(path, name)
				if path_name.endswith(ext) and (name.split('.')[-2] == fname):
					return path_name

	def codec_path(codec):
		path = get(codec)
		if not os.path.isfile(path):
			gtk.gdk.threads_enter()
			message = _('Codec\n <b>%s</b>\nmissing') %path
			show_dialog(message)
			glade.get_widget('stop_button').set_sensitive(False)
			if len(Conversation.task_list) > 0:
				glade.get_widget('start').set_sensitive(True)
			gtk.gdk.threads_leave()
		else:
			return True

	def file_not_found():
		gtk.gdk.threads_enter()
		message = (_('File \n<b>%s</b>\nnot found'
							) %bin_file)
		show_dialog(message)
		if len(Conversation.task_list) > 0:
			glade.get_widget('start').set_sensitive(True)
		gtk.gdk.threads_leave()

	if not os.path.isdir(get('tmp_dir')):
		gtk.gdk.threads_enter()
		message = (_('Temp dir \n<b>%s</b>\nnot found'
							) %get('tmp_dir'))
		show_dialog(message)
		glade.get_widget('stop_button').set_sensitive(False)
		if len(Conversation.task_list) > 0:
			glade.get_widget('start').set_sensitive(True)
		gtk.gdk.threads_leave()
		return

	folder, dic = parametrs
	treeview = glade.get_widget('job queue')
	model = treeview.get_model()
	all_tr = model.iter_n_children(model.get_iter(0))
	'''list tracks for decoder'''
	rowl = ''
	for n in range(model.iter_n_children(model.get_iter(0))):
		if model[0,n][3]:
			rowl += str(model[0,n][0]) + ','
	dic['trlist'] = rowl[:-1]
	dic['all_tr'] = all_tr
	for n in range(all_tr):
		if model[0,n][3]:
			dic[n+1] = model[0,n][1]
	clear_root_iter(glade)
	Conversation.job_name = '%s - %s' %(dic['performer'], dic['album'])
	gtk.gdk.threads_enter()
	progressbar2=glade.get_widget('progressbar2')
	progressbar2.set_fraction(0)
	progressbar2.set_text(
		'%s   in queue:%s' %(Conversation.job_name, len(Conversation.task_list)))
	gtk.gdk.threads_leave()
	set_fraction_progressbar1(0)
	'''decode to tmpdir'''
	tmpdir = tempfile.mkdtemp(prefix='gcue2tracks', dir=get('tmp_dir'))
	set('tmpdir', tmpdir)
	if 'bin_files' in dic:
		'''tracks + cue'''
		for n in rowl.split(','):
			if n is not '':
				bin_file = os.path.join(folder, dic['bin_files'][int(n) - 1])
				if not os.path.isfile(bin_file):
					bin_file = find_bin(folder, dic['bin_files'][int(n) - 1])
					if not bin_file:
						file_not_found()
						return
				command = get_command('split-track' + n)
				if command is None:
					return
				process(command.encode('utf-8'), dic, False,
					text = _('Decoding to wav "%s" (%d/%s) ')
					%(dic[int(n)], int(n), all_tr))
				gtk.gdk.threads_enter()
				progressbar2 = glade.get_widget('progressbar2')
				progressbar2.set_fraction(progressbar2.get_fraction() +
					2*(1.0/(2 + len(dic['trlist'].split(','))))
					/len(dic['trlist'].split(',')))
				gtk.gdk.threads_leave()
	else:
		f=popen2.Popen4('cuebreakpoints "%s" > %s/cuebreakpoints' %
			(dic['filename'], tmpdir))
		bin_file = os.path.join(folder, dic['bin_file'])
		'''file exits?'''
		if not os.path.isfile(bin_file):
			file_not_found()
			return
		command = get_command()
		if command is None:
			return
		process(command, dic, True, text = _('Decoding to wav '))

		'''split tracks'''
		if Conversation.value == (_('Interrupted')):
			clean_tmp(tmpdir)
			return
		if Conversation.value == 'error':
			print 'decode error'
			clean_tmp(tmpdir)
			return
		command = ('shnsplit -x "%s" '
				'-o "wav ext=wav shntool" '
				'-d "%s" '
				'-f "%s/cuebreakpoints" %s/wav.wav' %
				(dic['trlist'], tmpdir, tmpdir, tmpdir))
		process(command.encode('utf-8'), dic, True
									, text = _('split tracks  '))

	'''encoding tracks'''
	encoder(tmpdir, dic)

	'''movie encoded files'''
	a = Copy_result(tmpdir, dic)
	a = a.run()

def track_light(path, filename, glade):
	'''get track light'''
	filename = filename.encode('utf-8')
	path = path.encode('utf-8')
	os.chdir(path)
	f = popen2.Popen4(
		'cuebreakpoints "%s"' % glade.get_widget('filename').get_text()
		)
	fromchild = f.fromchild.readline()
	list = []
	start = 0
	len1 = ''
	while fromchild:
		fromchild = fromchild.replace('\n', '')
		start,len1 = pars(fromchild, start, len1)
		list.append(len1)
		fromchild = f.fromchild.readline()
	f = popen2.Popen4('shnlen -q "%s/%s"' % (path, filename))
	fromchild = f.fromchild.readlines()
	light = fromchild[1].strip().split(' ')[0]
	start,len1 = pars(light, start, len1)
	list.append(len1)
	return list,light

def pars(fromchild, start, len1):
	a1=string.find(fromchild, ':')
	if a1 != -1:
		min = int(fromchild[:a1])
		sec = int(fromchild[(a1+1):(a1+3)])
		dif = min*60+sec-start
		secs = str(dif-((dif/60)*60))
		if len(secs) < 2:
			secs = '0' + secs
		len1 = '%s:%s'% (str(dif/60), secs)
		start = min*60+sec
	return start, len1

def col0_edited_cb(cell, path, new_text, model ):
	#print "Change '%s' to '%s'" % (model[path][1], new_text)
	model[path][1] = new_text
	return

def col1_toggled_cb(cell, path, model ):
	a = model[path][3] = not model[path][3]
	treeview = glade.get_widget('job queue')
	iter = model.get_iter(path)
	s = model.iter_depth(iter)
	if s is not 0:
		return
	for n in range(model.iter_n_children(model.get_iter(path[0]))):
		model[int(path[0]),n][3] = a

def clean_tmp(tmpdir):
	for name in os.listdir(tmpdir):
		path_name = os.path.join(tmpdir, name)
		os.remove(path_name)
	os.rmdir(tmpdir)

def headerClick(TreeViewColumn, Column):
	print 'click' , Column


def clear_root_iter(glade):
	treeview = glade.get_widget('job queue')
	model = treeview.get_model()
	iter_root = model.get_iter_root()
	if iter_root is None:
		return
	gtk.gdk.threads_enter()
	model.remove(iter_root)
	if len(model) ==0:
		glade.get_widget('del_task').set_sensitive(False)
	else:
		treeview.set_cursor(0)
	gtk.gdk.threads_leave()

def encoder(tmpdir, dic):
	def getvar(file_name):
		level = dic['level']

		if codec =='flac':
			arg = 'flac -T TITLE="%s" -T ALBUM="%s" -T TRACKNUMBER=%s \
			-T ARTIST="%s" -T GENRE="%s" -T DATE="%s" \
			-T DESCRIPTION="gCue2tracks" -T COMPOSER="%s" ' % (
			title, dic['album'], trac_number,
			dic['performer'], dic['genre'],
			dic['date'], dic['composer'])
			if level =='mid':
				arg += '-5 '
			else:
				arg += '--%s ' %level

		if codec =='ogg':
			arg = 'oggenc -a "%s" -d "%s" -G "%s" -l "%s" -N "%s" -t "%s" -c "%s"' % (
					dic['performer'], dic['date'], dic['genre'], dic['album']
					, trac_number, title, 'DESCRIPTION=gCue2tracks')

			if dic['bitratebtn']:
				if dic['VBR']:
					arg += ' -b %s ' %dic['bitrate']
				else:
					arg += ' --managed -b %s -M %s ' % (dic['bitrate'], dic['bitrate'])
			else:
				arg += ' -q %s ' %dic['quality']

		if codec =='mp3':
			arg = 'lame --id3v2-only --ta "%s" --tt "%s" --tl "%s" --ty "%s" --tc "%s" \
				--tn "%s/%s" --tg "%s" --nohist' % (
				dic['performer'], title, dic['album'], dic['date'], 'gCue2tracks'
				, trac_number, dic['all_tr'], dic['genre'])
			if get('mp3advance'):
				if dic['bitratebtn']:
					if dic['VBR']:
						arg += ' -v -B %s -q %s ' % (dic['bitrate'], dic['quality'])
					else:
						arg += ' -b %s -q %s ' % (dic['bitrate'], dic['quality'])
			else:
				if dic['bitratebtn']:
					if dic['VBR']:
						arg += ' -v -B %s ' %dic['bitrate']
					else:
						arg += ' -b %s ' %dic['bitrate']
				else:
					arg += ' -q %s ' %dic['quality']

		if codec =='wv':
			arg = 'wavpack -w "Title=%s" -w "Artist=%s" -w "Album=%s" '\
				'-w "Track=%s/%s" -w "Composer=%s" -w "Comment=gCue2tracks" '\
				'-w "Year=%s" -w "Genre=%s" ' % (
				title, dic['performer'], dic['album'],
				trac_number, dic['all_tr'], dic['composer'],
				dic['date'], dic['genre'])
			if level =='fast':
				arg +='-f '
			if level =='best':
				arg +='-hh '
			if level =='mid':
				arg +='-h '

		if codec =='ape':
			arg = 'mac %s %s ' % (file_name, file_name + '.ape')
			if level =='fast':
				arg +='-c1000 '
			if level =='best':
				arg +='-c4000 '
			if level =='mid':
				arg +='-c2000 '
			return arg

		arg += file_name
		return arg

	if Conversation.value == (_('Interrupted')):
		return
	if Conversation.value == 'error':
		print 'split error'
		return
	tmp_file_list = []
	tr_list = dic['trlist'].split(',')
	tr_to_enc = str(len(tr_list))
	print 'start encode'
	for name in os.listdir(tmpdir):
		if name.startswith('split-track'):
			file_name = os.path.join(tmpdir, name)
			tmp_file_list.append(file_name)
	tmp_file_list.sort()

	n = 0
	for file_name in tmp_file_list:
		trac_number = tr_list[n]
		title = dic[int(trac_number)]
		text = _('Encoding "%s" (%s/%s)  ') % (
				title, str(n+1), tr_to_enc)
		print text
		codec = dic['codec']
		command = getvar(file_name)
		if codec =='wv':
			process(command, dic, text = text)
		process(command, dic, True, text = text)
		if Conversation.value == 'error' or Conversation.value == (_('Interrupted')):
			return
		n +=1

def process(command, dic, progr = None, text = ''):

	def ss(a, b, n, fraction):
		b += a
		if a == '%':
			c = (b[-7:-1]).split(' ')
			try:
				c[-1] = c[-1].replace(',','.').replace('[','').replace('(','')
			except :
				pass
			try:
				n = float(c[-1])
			except :
				pass
			b = '0000000'

		progres = n/100.0
		if progres > fraction:
			set_fraction_progressbar1(progres)
			set_text_progressbar1('%s%s%s' %(text, str(n), '%'))
			fraction = progres
		if progres < fraction:
			set_fraction_progressbar1(0)
			fraction = 0
		return b, n, fraction

	if QUIET1:
		proc1 = popen.Popen4(command)
		while proc1.poll() == -1:
			sys.stdout.write(proc1.fromchild.read(1))
		if proc1.poll() == 0:
			Conversation.value = 'complete'
			return
	if Conversation.value == (_('Interrupted')):
		return
	if Conversation.value == 'error':
		print ' error'
		return
	fraction = 0
	all_tr = dic['all_tr']
	tr_to_enc = len(dic['trlist'].split(','))
	set_text_progressbar1(text)
	progressbar2 = glade.get_widget('progressbar2')
	try:
		Conversation.value = 'in process'
		proc1 = popen2.Popen4(command)
		Conversation.pid = proc1.pid
		n = 0
		b = '0000000'
		while proc1.poll() == -1:
			b, n, fraction = ss(proc1.fromchild.read(1), b, n, fraction)
		while proc1.fromchild.read(1):
			b, n, fraction = ss(proc1.fromchild.read(1), b, n, fraction)
		if proc1.poll() not in [256,0,-1]:
			set_fraction_progressbar1(0.0)
			if proc1.poll() == 9:
				set_text_progressbar1(_('Interrupted'))
				Conversation.value = (_('Interrupted'))
			else:
				set_text_progressbar1(_('Error'))
				Conversation.value = 'error'
		elif proc1.poll()==0:
			if progr:
				gtk.gdk.threads_enter()
				progressbar2.set_fraction(progressbar2.get_fraction() +
											(1.0/(2 + tr_to_enc)))
				gtk.gdk.threads_leave()
			set_fraction_progressbar1(0)
			Conversation.value = 'complete'
	except :
		Conversation.value = 'error'
		print 'error in ' + self.getName() + command

class Copy_result():

	def __init__(self, tmpdir, dic):
		self.tmpdir = tmpdir
		self.dic = dic

	def run(self):
		if Conversation.value == (_('Interrupted')):
			clean_tmp(self.tmpdir)
			return
		if Conversation.value == 'error':
			print 'cleaning temp'
			clean_tmp(self.tmpdir)
			return
		print 'start copy file'
		if self.dic['codec'] =='mp3' and get('mp3_utf'):
			# 'python-mutagen'
			set_text_progressbar1(_('Convert tag to UTF-8'))
			for root,dirs,files in os.walk(self.tmpdir):
				for f in files:
					if f.endswith('mp3'):
						conv = 'mid3iconv -e UTF-8 "%s/%s"' % (root, f)
						proc1 = popen2.Popen4(conv)
						proc1.wait()

		dic = {
			'%A':self.dic['album'],
			'%a':'Album disc number',
			'%P':self.dic['performer'],
			'%D':self.dic['date'],
			'%G':self.dic['genre'],
			'%t':'Track title',
			'%p':self.dic['performer'], '%g':self.dic['genre'],
			'%n':'%name', '%N':'Track number'
			}
		if self.dic['date'] is '':
			dic['%D'] = 'unknown'
		format = get('format')
		for n in dic:
			try:
				format = format.replace(n,dic[n])
			except:
				pass
		newdir = format[:format.rfind('/')]
		try:
			set_text_progressbar1(_('Create folder'))
			newdir = self.dic['folder'] + newdir
			os.makedirs(newdir)
		except OSError, (errno, strerror):
			print 'OSError(%s): %s' % (errno, strerror)

		newname_ = format[format.rfind('/') + 1:]
		tr_list = self.dic['trlist'].split(',')
		tmp_file_list = []
		for name in os.listdir(self.tmpdir):
			if name.endswith(self.dic['codec']) and name.startswith('split'):
				tmp_file_list.append(name)
		tmp_file_list.sort ()

		os.chdir(self.tmpdir)
		n = 0
		filtr = re.compile(r"[?\\*:><\"\|]") # filename filter ?  \ * : >< " |
		filename_filter = get('filename_filter')
		for file_name in tmp_file_list:
			self.trac_number = tr_list[n]
			self.title = self.dic[int(self.trac_number)]
			try:
				newname = newname_.replace('Track title', self.title)
				newname = newname.replace('%name', str(int(self.trac_number)))
			except:
				pass
			try:
				newname = newname.replace('Track number', self.trac_number)
			except:
				pass
			newname += '.%s' %self.dic['codec']
			# replace ? / \ * : >< " | in filenames
			if '/' in newname:
				newname = newname.replace('/', '_')
			if filename_filter:
				newname = filtr.sub('_', newname)

			os.rename(file_name, newname)
			set_text_progressbar1(_('Taging and copy %s' %newname))
			print newname, '=>> ' + newdir
			shutil.move(newname, newdir)
			n += 1

		if get('copy_image') and self.dic['filename'] != newdir:
			'''copy image files '''
			set_text_progressbar1(_('Copy image files '))
			import mimetypes
			copy_from = os.path.dirname(self.dic['filename'])
			mimetypes.init()
			for root, dirs, files in os.walk(copy_from):
				for name in dirs:
					if name not in newdir:
						try:
							os.mkdir(os.path.join(newdir, name))
						except OSError, (errno, strerror):
							pass#print 'OSError(%s): %s (%s)' \
							#% (errno, strerror, os.path.join(newdir, name))
				for name in files:
					filetype = mimetypes.guess_type(name)[0]
					if type(filetype) is str:
						filetype = filetype.split('/')[0]
						if filetype =='image':
							try:
								shutil.copy(
								os.path.join(root, name), newdir + root.replace(copy_from, ''))
							except:
								pass
			for root, dirs, files in os.walk(newdir):
				for name in dirs:
					if os.listdir(os.path.join(root, name)) == []:
						os.rmdir(os.path.join(root, name))
		set_text_progressbar1(_('Complete'))
		del dic


class Conversation(threading.Thread):

	def __init__(self, folder, task_list = None):
		threading.Thread.__init__(self)
		self.folder = folder
		self.task_list = task_list
		self.job_up = glade.get_widget('job_up')
		self.job_down = glade.get_widget('job_down')
		Conversation.value = None

	def run(self):
		while Conversation.task_list:
			task = Conversation.task_list.pop(0)
			if len(Conversation.task_list) == 1:
				self.job_up.set_sensitive(False)
				self.job_down.set_sensitive(False)
			start(Conversation.task_parametrs[task])
			if Conversation.value == (_('Interrupted')):
				print Conversation.value
				break
		Conversation.task_number = 0
		gtk.gdk.threads_enter()
		glade.get_widget('progressbar2').set_text ('  ')
		glade.get_widget('stop_button').set_sensitive(False)
		gtk.gdk.threads_leave()

	def stop(self):
		return Conversation.pid





