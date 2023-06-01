# bard-prompt: Utils for CLI use of bard, with logging and stuff

## Installation

1. Set up a venv. At present this is hard-coded in `env` as `bard`
1. Copy env-example to env and edit it to add your key, as per the `bardapi` instructions.
1. Activate your venv
1. Install `bardapi` from its github repo wherever that is... into your venv.

## About

`bard-prompt` is a bash wrapper around `bard-prompt.py`. It checks if the venv is active and enables it if needed

## bard-prompt usage:

1. `bard-prompt {text}`
1. `somecommand | bard-prompt` (Or some other way of getting it into stdin)

## bard-log usage (it just lists the log files):

1. `bard-log`
