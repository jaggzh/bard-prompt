import tempfile
import subprocess

# stg.execute_first_in_list()
# Execute the first program found in bin_list
# If all fail, try those in fallbacks (list)
# args is None or a list of params to the executable
# Return subprocess errorcode (0 on success of course)
def execute_first_in_list(bin_list, fallbacks=None, args=None):
	for bin in (bin_list + fallbacks if fallbacks is not None else bin_list):
		try:
			process = subprocess.run([bin] + args if args is not None else [bin])
			return process.returncode  # return the error code of the process
		except FileNotFoundError:  # catch specific exception
			pass
	return None  # return None if no executable found in the list

