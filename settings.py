import os, sys
import inspect

def get_script_final_dir():
	if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
		path = os.path.abspath(sys.executable)
	else: path = inspect.getabsfile(get_script_final_dir)
	path = os.path.realpath(path)
	return os.path.dirname(path)

our_dir = get_script_final_dir()
dir_log=os.path.join(our_dir, 'data/log')

# set your __Secure-1PSID in environment
# or os.environ['_BARD_API_KEY']="xxxxxxxx"
envkey_name='_BARD_API_KEY'

editors=['vim', 'nano']
editors_json=['jless', 'vim']

if envkey_name not in os.environ:
	print(f"{bred}Error: Missing env var '{envkey_name}'{rst}", file=sys.stderr)
	exit(1)
if not os.path.isdir(dir_log):
	os.makedirs(dir_log, exist_ok=True)

