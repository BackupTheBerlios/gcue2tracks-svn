#!/bin/bash
intltool-update --pot -g templates
msgmerge -U ru.po '/home/test/deb пакеты/gcue2tracks-0.1/po/templates.pot' 
msgmerge -U es.po '/home/test/deb пакеты/gcue2tracks-0.1/po/templates.pot'