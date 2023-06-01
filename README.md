# bard-prompt: Utils for CLI use of bard, with logging and stuff

## Installation

1. Create a venv for this project
    1. ie. `python3 -m venv 'somedir/bardprompt'`
1. Copy env-example to env and edit it. Follow its instructions.
1. Activate your new venv for the next step...
1. Install `bardapi` from its github repo... wherever that is

## Notes:

`bard-prompt` is a bash wrapper around `bard-prompt.py`. It checks if the venv is active and enables it if needed

## bard-prompt usage:

1. `bard-prompt {text}`
1. `somecommand | bard-prompt` (Or some other way of getting it into stdin)

## bard-log usage (it just lists the log files):

1. `bard-log`
