# Makefile for program source directory in GNU NLS utilities package.


GETTEXT_PACKAGE = gajim
PACKAGE = gajim
VERSION = 0.12-beta1

SHELL = /bin/sh

srcdir = .
top_srcdir = ..
top_builddir = ..


prefix = /usr/local
exec_prefix = ${prefix}
datadir = ${datarootdir}
datarootdir = ${prefix}/share
libdir = ${exec_prefix}/lib
DATADIRNAME = share
itlocaledir = $(prefix)/$(DATADIRNAME)/locale
subdir = po
install_sh = $(SHELL) /home/test/gajim/install-sh
# Automake >= 1.8 provides /bin/mkdir -p.
# Until it can be supposed, use the safe fallback:
mkdir_p = $(install_sh) -d

INSTALL = /usr/bin/install -c
INSTALL_DATA = ${INSTALL} -m 644

GMSGFMT = /usr/bin/msgfmt
MSGFMT = /usr/bin/msgfmt
XGETTEXT = /usr/bin/xgettext
INTLTOOL_UPDATE = /usr/bin/intltool-update
INTLTOOL_EXTRACT = /usr/bin/intltool-extract
MSGMERGE = INTLTOOL_EXTRACT=$(INTLTOOL_EXTRACT) srcdir=$(srcdir) $(INTLTOOL_UPDATE) --gettext-package $(GETTEXT_PACKAGE) --dist
GENPOT   = INTLTOOL_EXTRACT=$(INTLTOOL_EXTRACT) srcdir=$(srcdir) $(INTLTOOL_UPDATE) --gettext-package $(GETTEXT_PACKAGE) --pot

ALL_LINGUAS = 

PO_LINGUAS=$(shell if test -r $(srcdir)/LINGUAS; then grep -v "^\#" $(srcdir)/LINGUAS; fi)
all:
	echo $(srcdir)

