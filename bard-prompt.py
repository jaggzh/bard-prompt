#!/usr/bin/env python
from bardapi import Bard
import bardapi, os, sys, ipdb, tempfile, json
from bansi import *
from datetime import datetime
import time
import argparse
import re
import requests
import pickle

ua='Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
envkey_name='_BARD_API_KEY' # This is used both internally for sessions, and externally
                            # by the Bard-API python module
args=None
dir_log=None
dir_sessions=None
losession_name=None
losession_fn=None
losession_headers = {
	"Host": "bard.google.com",
	"X-Same-Domain": "1",
	"User-Agent": ua,
	"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
	"Origin": "https://bard.google.com",
	"Referer": "https://bard.google.com/",
}
token=None

def validate_session(name):
	if '/' in name or '../' in name or name.startswith('.'):
		raise ValueError(f"Invalid session name: '{name}'")

def init():
	global dir_log
	global args
	global losession_name, losession_fn
	global token
	our_dir = os.path.dirname(os.path.abspath(__file__))
	dir_log=os.path.join(our_dir, 'data/log')
	dir_sessions=os.path.join(our_dir, 'data/sessions')

	if envkey_name not in os.environ:
		printe(f"{bred}Error: Missing env var '{envkey_name}'{rst}")
		exit(1)
	token = os.getenv(envkey_name)
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--test", help="Test mode. Don't send out request",
						action="store_true")
	parser.add_argument("-v", "--verbosity", action="count",
						default=0, help="Increase output verbosity")
	parser.add_argument("-r", "--remove", action="store_true",
						help="Remove session data before starting (use with -s)")
	parser.add_argument("-s", "--session", type=str,
						help="Use continuing session id")
	parser.add_argument('text', nargs='?', help='Text or Filename. Without this we read from stdin')
	args = parser.parse_args()
	if args.remove and not args.session:
		print("-r (remove) needs -s (session)", file=sys.stderr)
		sys.exit(1)
	if not os.path.isdir(dir_log):
		os.makedirs(dir_log, exist_ok=True)
	if args.session is not None:
		validate_session(args.session)
		losession_name = args.session
		if not os.path.isdir(dir_sessions):
			os.makedirs(dir_sessions, exist_ok=True)
		losession_fn = os.path.join(dir_sessions, losession_name)

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
		printe("Wrote log to:")
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

def bard_prompt(prompt=None, args=None): # uses global session variables
	if prompt is None or args is None:
		raise ValueError('bard_prompt() requires prompt= and args=')
	if losession_name is not None:
		print(f"Using session {losession_name}")
		session = requests.session()
		if not os.path.isfile(losession_fn):
			printe(f"Starting local-session: {losession_fn}")
			session.headers = losession_headers  # New session
		else:
			if args.remove:                    # ALSO New session
				os.unlink(losession_fn)
				printe(f"Local-session removed: {losession_fn}")
				session.headers = losession_headers
			else:
				printe(f"Loading local-session: {losession_fn}")
				with open(losession_fn, 'rb') as f:
					session.cookies.update(pickle.load(f))
		session.cookies.set("__Secure-1PSID", token)
		bard = Bard(token=token, session=session, timeout=30)
		response = bard.get_answer(prompt)
		with open(losession_fn, 'wb') as f:
			pickle.dump(session.cookies, f)
			printe(f"Local-session saved: {losession_fn}")
	else: # No losession_name (sessionless)
		response = Bard().get_answer(prompt)
	return response

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
		response = bard_prompt(prompt=in_txt, args=args)
		# printe("Yay, sending to bard")
	else:
		printe(f"{yel}Test mode. Making dummy request and logging it.{rst}")
		response = { 'nothing': 1 }
	if response is None:
		printe("{bred}Error, response from bard is None{rst}")
		raise(ValueError("Bard response is None"))
	log(in_txt, response)
	try:
		print(response['content'])
	except:
		printe("Error accessing response['content']")

if __name__ == '__main__':
	main()
