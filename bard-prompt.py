#!/usr/bin/env python
from bardapi import Bard
import bardapi, os, sys, ipdb, tempfile, json
from bansi import *
from datetime import datetime
import time
import argparse
import re

envkey_name='_BARD_API_KEY'
args=None
dir_log=None

def init():
	global dir_log
	global args
	our_dir = os.path.dirname(os.path.abspath(__file__))
	dir_log=os.path.join(our_dir, 'data/log')

	if envkey_name not in os.environ:
		printe(f"{bred}Error: Missing env var '{envkey_name}'{rst}")
		exit(1)
	if not os.path.isdir(dir_log):
		os.makedirs(dir_log, exist_ok=True)

	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--test", help="Test mode. Don't send out request",
						action="store_true")
	parser.add_argument("-v", "--verbosity", action="count",
						default=0, help="Increase output verbosity")
	parser.add_argument('text', nargs='?', help='Text or Filename. Without this we read from stdin')
	args = parser.parse_args()

def printe(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)
def exit(errno=None): sys.exit(0 if errno is None else 1)

def log_time_fmt():
	now = datetime.now()
	return now.strftime("%Y-%m-%d--%H:%M:%S.%f")[:-3]

def str_to_filestr(string):
	string = string.lower()
	string = re.sub(r'[^a-z0-9]+', '_', string)
	string = re.sub(r'_+', '_', string)
	string = re.sub(r'^_', '', string)
	return string

def get_summary(response, filename=False):
	summary=None
	try:
		summary = response['textQuery'][0]
		if filename: summary = str_to_filestr(summary)
	except:
		printe("Error accessing response['textQuery'][0]")
	return summary

def log(prompt, response):
	timestr=None
	while True:
		timestr=log_time_fmt()
		summary = get_summary(response, filename=True)
		if summary is not None:
			fn = os.path.join(dir_log, f"{timestr}--{summary}.json")
		else:
			fn = os.path.join(dir_log, f"{timestr}.json")
		if os.path.exists(fn):
			time.sleep(.01)
		else: break
	result = {
		'date': timestr,
		'prompt': prompt,
		'response': response,
		}
	pretty_result = json.dumps(result, indent=2)
	try:
		with open(fn, 'w') as F:
			F.write(pretty_result + '\n')
		printe("Wrote session to:")
		printe(f"{bcya}{fn}{rst}")
		printe('')
	except Exception as e:
		err_str = str(e)
		printe(f"{bred}Error writing to log {fn}: {errstr}{rst}")
		tmpdir = tempfile.gettempdir()
		tmpfile = os.path.join(tmpdir, "bard-last--fail.json")
		tmpfileerr = False
		os.umask(0o177)
		try:
			with open(tmpfile, 'w') as tmp:
				tmp.write(pretty_result + '\n')
		except:
			errmsg = f"{bred}Error writing to tmpfile {tmpfile}. Printing only to stdout{rst}"
			printe(errmsg)
			print(pretty_result, flush=True)
			printe(errmsg)

def main():
	init()
	response = None
	if args.text is None:
		print("Reading from stdin...", file=sys.stderr)
		in_txt = sys.stdin.read()
	else:
		in_txt = args.text
		if os.path.isfile(in_txt):
			in_fn = in_txt
			with open(in_txt, 'r') as F:
				in_txt = F.read()
			print(in_txt)
	if not args.test:
		response = Bard().get_answer(in_txt)
		# printe("Yay, sending to bard")
	else:
		printe(f"{yel}Test mode. Making dummy request and logging it.{rst}")
		response = { 'nothing': 1 }
	if response is None:
		printe("{bred}Error, response from bard is None{rst}")
		raise(ValueError("Bard response is None"))
	response['images'] = None
	# import ipdb; ipdb.set_trace(context=21); pass
	log(in_txt, response)
	try:
		print(response['content'])
	except:
		printe("Error accessing response['content']")

if __name__ == '__main__':
	main()
