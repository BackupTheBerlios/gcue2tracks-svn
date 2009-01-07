#!/usr/bin/python
#-*- coding: utf8 -*-
import os
try: # rename the process name to gCue2tracks
	import dl
	libc = dl.open('/lib/libc.so.6')
	libc.call('prctl', 15, 'gCue2tracks\0', 0, 0, 0)
except:
	pass

(
OPT_TYPE,
OPT_VAL,
OPT_DESC,
OPT_RESTART,
) = range(4)

opt_int = [ 'integer', 0 ]
opt_str = [ 'string', 0 ]
opt_bool = [ 'boolean', 0 ]
__options = {
	# name: [ type, default_value, help_string ]
	'savepath': [ opt_str, '' ],
	'codepage': [ opt_str, '' ],
	'mp3_utf': [ opt_bool, False ],
	'convert_cue': [ opt_bool, True ],
	'bitrait': [ opt_int, 128],
	'VBR': [ opt_bool, True ],
	'quality': [ opt_str, "7"],
	'qualitybtn': [ opt_bool, True ],
	'bitratebtn': [ opt_bool, False ],
	'same_folder': [ opt_bool, True ],
	'codec': [ opt_int, 0 ],
	'level': [ opt_int, 0 ],
	'format': [ opt_str, '/%P/%D - %A/%t' ],
	'open_folder': [ opt_str, os.path.expanduser('~') ],
	'save_folder': [ opt_str, os.path.expanduser('~') ],
	'cue2tracks': [ opt_bool, False ],
	'show_log': [ opt_bool, True ],
	'tmp_dir': [ opt_str, '/tmp' ],
	'ogg': [ opt_str, '/usr/bin/oggenc' ],
	'mp3': [ opt_str, '/usr/bin/lame' ],
	'mac': [ opt_str, '/usr/bin/mac' ],
	'flac': [ opt_str, '/usr/bin/flac' ],
	'wavpack': [ opt_str, '/usr/bin/wavpack' ],
	'wvunpack': [ opt_str, '/usr/bin/wvunpack' ],
	'filename_filter': [ opt_bool, False ],
	'mp3advance': [ opt_bool, False ],
	'disable_taging': [ opt_bool, False ],
	'tmpdir': [ opt_str, '/tmpfolder' ],
	'find_cue_folder' : [ opt_str, '' ],
	'copy_image' : [ opt_bool, False ],
}

def is_valid_int(val):
	try:
		ival = int(val)
	except:
		return None
	return ival

def is_valid_bool(val):
	if val == 'True':
		return True
	elif val == 'False':
		return False
	else:
		ival = is_valid_int(val)
		if ival:
			return True
		elif ival is None:
			return None
		return False
	return None

def is_valid_string(val):
	return val

def is_valid(type, val):
	if not type:
		return None
	if type[0] == 'boolean':
		return is_valid_bool(val)
	elif type[0] == 'integer':
		return is_valid_int(val)
	elif type[0] == 'string':
		return is_valid_string(val)
	else:
		return None

def write_line( fd, opt, value):
	if value is None:
		return
	value = value[1]
	 #convert to utf8 before writing to file if needed
	if isinstance(value, unicode):
		value = value.encode('utf-8')
	else:
		value = str(value)
	if isinstance(opt, unicode):
		opt = opt.encode('utf-8')
	s = ''
	s += opt
	fd.write(s + ' = ' + str(value) + '\n')

def write():
	(base_dir, filename) = os.path.split(conf_path + "/config")
	__tempfile = os.path.join(base_dir, '.' + filename)
	try:
		f = open(__tempfile, 'w')
	except IOError, e:
		return str(e)
	try:
		foreach(write_line, f)
	except IOError, e:
		return str(e)
	f.close()
	if os.path.exists(conf_path + "/config"):
		# win32 needs this
		try:
			os.remove(conf_path + "/config")
		except:
			pass
	try:
		os.rename(__tempfile, conf_path + "/config")
	except IOError, e:
		return str(e)
	os.chmod(conf_path + "/config", 0600)

def foreach( cb, data = None):
	for opt in __options:
		cb(data, opt, __options[opt])

def get(optname = None):
	if not optname:
		return __options.keys()
	if not __options.has_key(optname):
		return None
	return __options[optname][OPT_VAL]

def add_per(self, typename, name): # per_group_of_option
	if not self.__options_per_key.has_key(typename):
		return

	opt = self.__options_per_key[typename]
	if opt[1].has_key(name):
		# we already have added group name before
		return 'you already have added %s before' % name
	opt[1][name] = copy.deepcopy(opt[0])

def del_per(self, typename, name, subname = None): # per_group_of_option
	if not self.__options_per_key.has_key(typename):
		return

	opt = self.__options_per_key[typename]
	if subname is None:
		del opt[1][name]
	elif opt[1][name].has_key(subname):
		del opt[1][name][subname]

def set_per(self, optname, key, subname, value): # per_group_of_option
	if not self.__options_per_key.has_key(optname):
		return
	dict = self.__options_per_key[optname][1]
	if not dict.has_key(key):
		return
	obj = dict[key]
	if not obj.has_key(subname):
		return
	subobj = obj[subname]
	value = self.is_valid(subobj[OPT_TYPE], value)
	if value is None:
		return
	subobj[OPT_VAL] = value

def set(optname, value):
	if not __options.has_key(optname):
		return
	opt = __options[optname]
	value = is_valid(opt[OPT_TYPE], value)
	if value is None:
		return

	opt[OPT_VAL] = value

def read_line(line):
	index = line.find(' = ')
	var_str = line[0:index]
	value_str = line[index + 3:-1]
	set(var_str, value_str)


conf_path = os.path.expanduser('~') + "/.config/gCue2tracks"
if not os.path.isfile(conf_path + "/config"):
	if not os.path.isdir(conf_path):
		os.makedirs(conf_path)
	fd = open(conf_path + "/config", 'w')
	fd.close()
	print "create config" ####
try:
	fd = open(conf_path + "/config")
except:
	if os.path.exists(conf_path + "/config"):
		#we talk about a file
		print _('error: cannot open %s for reading') % conf_path + "/config"
for line in fd.readlines():
	# read config
	try:
		line = line.decode('utf-8')
	except UnicodeDecodeError:
		line = line.decode(locale.getpreferredencoding())
	read_line(line)
fd.close()
