from __future__ import print_function
import sys

# Some color codes for terminals.
# You just print the text and color codes, and print rst to
# send the color reset sequence.

# The color sequence names are in the first bit of code below.

# Usually, just use with something like:
#   from jaggz.ansi import *  # Convenient! Imports into global namespace
#                             # wonders like: red, bred, yel, bgblu, etc.
#   print(red, "Hi, ", blu, username, rst, sep="")
# This mess by jaggz.h who periodically reads his gmail.com

# I usually import some routines from my utils.py:
# pfp() (print..plain) is print() with sep='', so I don't get spaces
# between my text and ansi sequences
#
# def pf(*x, **y):    # Print-flush
# 	print(*x, **y)
# 	sys.stdout.flush()
# def pfp(*x, **y):   # Print-flush, plain (no separator)
# 	y.setdefault('sep', '')
# 	print(*x, **y)
# 	sys.stdout.flush()
# def pfl(*x, **y):   # Print-flush, line (ie. no newline)
# 	y.setdefault('end', '')
# 	print(*x, **y)
# 	sys.stdout.flush()
# def pfpl(*x, **y):  # Print-flush, plain, line (no sep, no NL)
# 	y.setdefault('sep', '')
# 	y.setdefault('end', '')
# 	print(*x, **y)
# 	sys.stdout.flush()

esc="^["
esc="\033"
bgbla=esc + "[40m"
bgred=esc + "[41m"
bggre=esc + "[42m"
bgbro=esc + "[43m"
bgblu=esc + "[44m"
bgmag=esc + "[45m"
bgcya=esc + "[46m"
bggra=esc + "[47m"
bla=esc + "[30m"
red=esc + "[31m"
gre=esc + "[32m"
bro=esc + "[33m"
blu=esc + "[34m"
mag=esc + "[35m"
cya=esc + "[36m"
gra=esc + "[37m"
bbla=esc + "[30;1m"
bred=esc + "[31;1m"
bgre=esc + "[32;1m"
yel=esc + "[33;1m"
bblu=esc + "[34;1m"
bmag=esc + "[35;1m"
bcya=esc + "[36;1m"
whi=esc + "[37;1m"
rst=esc + "[0;m"
chide=esc + "[?25l"
cshow=esc + "[?25h"

def apfl(*x, **y):
	y.setdefault('sep', '')
	y.setdefault('end', '')
	print(*x, **y)
	sys.stdout.flush()


aseq_rg = [16,52,58,94,100,136,142,178,184,220]
aseq_rb = [16,52,53,89,90,126,127,163,164,200]
aseq_gb = [16,22,23,29,30,36,37,43,44,50]
aseq_r  = [16,52,88,124,160,196]
aseq_g  = [16,22,28,34,40,46]
aseq_b  = [16,17,18,19,20,21]
aseq_gr = [232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255]

def a256fg(a):
	return esc + "[38;5;" + str(a) + "m";
def a256bg(a):
	return esc + "[48;5;" + str(a) + "m";
def aseq_norm(seq, i): # Takes sequence and a value from [0-1]
	return seq[int((len(seq)-2) * i)+1]

def a24fg(r,g,b):
	return "\033[38;2;"+str(r)+";"+str(g)+";"+str(b)+"m"
def a24bg(r,g,b):
	return "\033[48;2;"+str(r)+";"+str(g)+";"+str(b)+"m"

def a24fg_rg(v): # 0-1 for red-green
	return a24fg(int(255.0*(1-v)), int(255.0*v), 0)
def a24bg_rg(v): # 0-1 for red-green
	return a24bg(int(255.0*(1-v)), int(255.0*v), 0)

def a24fg_ry(v): # 0-1 for red-green
	return a24fg(255, int(255.0*v), 0)
def a24bg_ry(v): # 0-1 for red-green
	return a24bg(255, int(255.0*v), 0)

# outputs colorized letters based on corresponding same-length
# list of values, using sequence codes from aseq
# skips first color (being too dark) by using aseq_norm()
# s:      String input (might work with anything where s[i] is printable)
# values: List of numerical values. Same length as s.
#         These are the magnitudes of the colors
#         -- the range is calculated linearly between min() and max()
# aseq:   The ansi color sequence (ex. aseq_rb). See those in this file.
# bg=True:  To set background instead of fg. (Default: False)
# color:  Optionally set a fixed color for fg or bg
#         Use the color variables from this file, like:
#         red, bred (brightred), bgred, etc.
def str_colorize(s, values, aseq, bg=False, color=None):
	minv = min( values )
	maxv = max( values )
	for i in range(len(s)):
		val = values[i]
		norm = (float(val)-minv)/(maxv - minv)
		ansival=aseq_norm(aseq, norm)
		if not color == None: print(color, end='')
		if bg:
			ansistr=a256bg(ansival)
		else:
			ansistr=a256fg(ansival)
		print(ansistr, s[i], sep='', end='')
	print(rst)

def uncolor():
	global bgbla, bgred, bggre, bgbro, bggre, bgmag, bgcya, bggra
	global bla, red, gre, bro, gre, mag, cya, gra
	global bbla, bred, bgre, yel, bgre, bmag, bcya, whi
	global rst
	
	bgbla, bgred, bggre, bgbro, bggre, bgmag, bgcya, bggra = [""]*8
	bla, red, gre, bro, gre, mag, cya, gra = [""]*8
	bbla, bred, bgre, yel, bgre, bmag, bcya, whi = [""]*8
	rst = ""

def get_linux_termsize_xy(): # x,y
	return get_linux_terminal()

def get_linux_terminal(): # x,y
	import os
	env = os.environ
	def ioctl_GWINSZ(fd):
		try:
			import fcntl, termios, struct, os
			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
		'1234'))
		except:
			return
		return cr
	cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
	if not cr:
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			cr = ioctl_GWINSZ(fd)
			os.close(fd)
		except:
			pass
	if not cr:
		cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

		### Use get(key[, default]) instead of a try/catch
		#try:
		#	cr = (env['LINES'], env['COLUMNS'])
		#except:
		#	cr = (25, 80)
	return int(cr[1]), int(cr[0])

import sys
def gy(sy):
	apfl(esc + "[{}H".format(sy))
	sys.stdout.flush()
def gxy(sx,sy):
	apfl(esc + "[{};{}H".format(sy,sx))
	sys.stdout.flush()
def gyx(sy,sx):
	apfl(esc + "[{};{}H".format(sy,sx))
	sys.stdout.flush()
def cls():
	apfl(esc + "[2J")
	sys.stdout.flush()
def gright(v=None):
	if v is none: apfl(esc + "[C")
	else: apfl(esc + f"[{v}C")
def gleft(): apfl(esc + "[D")
def gup(): apfl(esc + "[A")
def gdown(): apfl(esc + "[B")

