#!/usr/bin/env python3
from bardapi import Bard
import bardapi, os, sys, ipdb, tempfile, json
from bansi import *
from datetime import datetime
import time
import argparse
import re
import settings as stg
import common as com
import subprocess

args=None

def init():
	global args

	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--test", help="Test mode. Don't send out request",
						action="store_true")
	parser.add_argument("-v", "--verbosity", action='count',
						default=0, help="Increase output verbosity")
	parser.add_argument("-e", "--edit-prompt", action='store_true',
						help="Use editor for prompt")
	parser.add_argument('text', nargs='*', help='Text (may be separate args), or Filename. Without this we read from stdin')
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
			fn = os.path.join(stg.dir_log, f"{timestr}--{summary}.json")
		else:
			fn = os.path.join(stg.dir_log, f"{timestr}.json")
		if os.path.exists(fn):
			time.sleep(.01)
		else: break
	response['images'] = None
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

def prompt_editor(args=None, initial_text=None):
	old_mask = os.umask(0o077)
	tmpfile = tempfile.NamedTemporaryFile(delete=False).name
	# Write initial text to the temp file
	with open(tmpfile, 'w') as file:
		if initial_text is not None:
			file.write(initial_text)
	os.umask(old_mask)
	rc = com.execute_first_in_list(stg.editors, args=[tmpfile])
	if rc is None:
		print("No editor found.", file=sys.stderr)
		return None
	else:
		with open(tmpfile, 'r') as file:
			text_content = file.read()
		os.remove(tmpfile)
		return text_content

def print_response(response):
	string = response['content']
	command = "less -F"
	process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE)
	process.stdin.write(string.encode("utf-8"))
	process.stdin.close()
	process.wait()

# def print_response(response):
# 	content = response['content']
# 	# Open a pipe to the `less` command
# 	process = subprocess.Popen(['less', '-F'], stdin=subprocess.PIPE, universal_newlines=True)
	
# 	# Write the content to `less`
# 	try:
# 		process.stdin.write(content)
# 	except BrokenPipeError:
# 		# The pipe is closed (e.g., by q) before all data is written. This can be ignored.
# 		pass
# 	finally:
# 		# Close the input stream to `less`.
# 		process.stdin.close()

def main():
	init()
	response = None
	# User specified some non-option text
	# 1. It might be a filename (must be a single argument then)
	# 2. It could be one or more strings (we join with spaces and use as our text)
	#    2a. If they specify -e to edit, we'll pop up the editor on that
	in_txt = None
	# print(f"args.text type: {type(args.text)}")
	# print(f"     args.text: {args.text}")
	# print(f" len args.text: {len(args.text)}")
	# exit()
	# import ipdb; ipdb.set_trace()
	if args.text is not None and len(args.text)>0:
		if len(args.text) == 1 and os.path.isfile(args.text[0]):
			in_fn = in_txt
			with open(in_txt, 'r') as F:
				in_txt = F.read()
			# print(in_txt)
		else:
			args.text = ' '.join(args.text)
			in_txt = args.text
		if args.edit_prompt:
			in_txt = prompt_editor(args=args, initial_text=args.text)
			if in_txt is None:
				print("Aborted.")
				exit(0)
	# User did NOT provide any text, but asked for the editor:
	elif args.edit_prompt:
		in_txt = prompt_editor(args=args)
		if in_txt is None:
			print("Aborted.")
			exit(0)
	else:
		print("Reading from stdin...", file=sys.stderr)
		in_txt = sys.stdin.read()
	
	if in_txt is None:
		raise ValueError(f"I'm confused and couldn't find any text to edit somehow")
	else:
		if not args.test:
			response = Bard().get_answer(in_txt)
			# printe("Yay, sending to bard")
		else:
			printe(f"{yel}Test mode. Making dummy request and logging it.{rst}")
			response = { 'nothing': 1 }
		if response is None:
			printe("{bred}Error, response from bard is None{rst}")
			raise(ValueError("Bard response is None"))
		log(in_txt, response)
		try:
			print_response(response)
		except:
			printe("Error accessing response['content']")

if __name__ == '__main__':
	main()
