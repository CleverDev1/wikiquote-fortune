#!/usr/bin/env python3

# wikiquote-fortune – Generate fortune cookies from Wikiquote
# Copyright © 2014  Mattias Andrée (maandree@member.fsf.org)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# 
# Note that output from this script is derivative work of Wikiquote
# and is therefore under the license used at Wikiquote.

import sys
import pyexpat
from subprocess import Popen, PIPE

# All modules are included in Python


show_ = sys.argv[1].replace(' ', '_')
show = show_.replace('_', ' ')
dateonly = (len(sys.argv) > 2) and (sys.argv[2] == 'date-only')


command = ['wget', 'http://en.wikiquote.org/wiki/%s' % show_, '-O', '-']
proc = Popen(command, stdout = PIPE, stderr = sys.stderr)
wiki = proc.communicate()[0]
if proc.poll() is None:
    proc.wait()
if not proc.returncode == 0:
    sys.exit(1)


if not dateonly:
    pass


history_url = None
def start_element(name, attrs):
    global history_url
    if name == 'a':
        if 'href' in attrs:
            val = attrs['href']
            val_ = val.replace('?', '&') + '&'
            if 'action=history' in val_.split('&'):
                if not val.startswith('/'):
                    sys.exit(1)
                history_url = 'http:' if val.startswith('//') else 'http://en.wikiquote.org'
                history_url += val

parser = pyexpat.ParserCreate()
parser.StartElementHandler = start_element

parser.Parse(wiki, 1)


if history_url is None:
    sys.exit(1)


command = ['wget', history_url, '-O', '-']
proc = Popen(command, stdout = PIPE, stderr = sys.stderr)
history = proc.communicate()[0]
if proc.poll() is None:
    proc.wait()
if not proc.returncode == 0:
    sys.exit(1)


on_mw_changeslist_date = False
def start_element(name, attrs):
    global on_mw_changeslist_date
    on_mw_changeslist_date = False
    if name == 'a':
        if ('class' in attrs) and (attrs['class'] == 'mw-changeslist-date'):
            on_mw_changeslist_date = True

def end_element(name):
    global on_mw_changeslist_date
    on_mw_changeslist_date = False

last_modified = None
def char_data(data):
    global last_modified
    if on_mw_changeslist_date and (last_modified is None):
        last_modified = data

parser = pyexpat.ParserCreate()
parser.StartElementHandler = start_element
parser.EndElementHandler = end_element
parser.CharacterDataHandler = char_data

parser.Parse(history, 1)


if last_modified is None:
    sys.exit(1)


(time, date) = last_modified.split(', ')
(day, month, year) = date.split(' ')


months = { 'January'   : '01'
         , 'February'  : '02'
         , 'March'     : '03'
         , 'April'     : '04'
         , 'May'       : '05'
         , 'June'      : '06'
         , 'July'      : '07'
         , 'August'    : '08'
         , 'September' : '09'
         , 'October'   : '10'
         , 'November'  : '11'
         , 'December'  : '12'
         }

day = ('0' + day)[-2:]
month = months[month]
year = year[-2:]

date = year + month + day
time = ('0' + time.replace(':', ''))[-4:]
version = date + time

with open('version', 'wb') as file:
    file.write(version.encode('utf-8'))
    file.flush()

