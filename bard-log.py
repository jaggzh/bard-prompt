#!/usr/bin/env python3
import os
from datetime import datetime
import sys
import os; import sys; import inspect;
import argparse
import subprocess
import settings as stg
import common as com
from bansi import *

def get_script_final_dir():
	if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
		path = os.path.abspath(sys.executable)
	else: path = inspect.getabsfile(get_script_final_dir)
	path = os.path.realpath(path)
	return os.path.dirname(path)

def getargs():
	parser = argparse.ArgumentParser(
	                prog='bard-log',
	                description='bard-prompt log examination util',
					)
	# parser.add_argument("-w", "--wide", help="make something wide", action="store_true")
	# parser.add_argument("-v", "--verbose", action="count",
	# 					default=0, help="increase output verbosity")
	parser.add_argument('last', nargs='?', type=int,
						help='Edit Nth from last file (starting at 1)')
	args = parser.parse_args()
	return args

def get_logs_file_mtime_size(dir=None):
	if dir is None: raise ValueError("No directory provided")
	files = os.listdir(dir)
	files_info = [(f, os.path.getmtime(os.path.join(dir, f)), os.path.getsize(os.path.join(dir, f))) \
				for f in files if os.path.isfile(os.path.join(dir, f))]
	files_info.sort(key=lambda x: x[1], reverse=False)
	return files_info

def edit_log_last_n(dir=None, n=1):
	files_info = get_logs_file_mtime_size(dir=dir)
	cnt = len(files_info)
	if cnt < 0: print("No logs"); return
	if cnt < n: print(f"Only {cnt} logs available. {n} is invalid."); return
	last_finfo = files_info[-n]
	path = os.path.join(dir, last_finfo[0])
	rc = com.execute_first_in_list(stg.editors_json,
	                                    fallbacks=[os.getenv('EDITOR')],
	                                    args=[path])
	if rc is None:
		print(f"No editor found in {editors_json} or env(EDITOR)",
			file=sys.stderr)
	else:
		print('')

def list_files(dir=None):
	if dir is None: raise ValueError("No directory provided")
	files_info = get_logs_file_mtime_size(dir=dir)
	cnt = len(files_info)
	if cnt < 1: print("No logs"); return
	max_filename_length = max(len(filename) for filename, _, _ in files_info)
	max_size_length = max(len(str(size)) for _, _, size in files_info)

	curi=cnt
	cntsize = len(str(cnt))
	for filename, mtime, size in files_info:
		time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
		print(f"{curi:<{cntsize}} {filename:<{max_filename_length}}  {size:<{max_size_length}}  {time_str}")
		curi -= 1
	print(f"Log count: {cnt}")

def main():
	args=getargs()
	our_dir = get_script_final_dir()
	dir_log=os.path.join(our_dir, 'data/log')

	print("Logs at:", dir_log)
	if args.last is not None:
		edit_log_last_n(dir=dir_log, n=args.last)
	else:
		list_files(dir_log)
	print("Logs at:", dir_log)
if __name__ == '__main__': main()
