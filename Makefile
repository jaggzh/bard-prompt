all:
	@echo 'Try: make vi'

vi:
	vim \
		Makefile \
		README.md \
		bard-prompt \
		bard-prompt.py \
		bard-log \
		settings.py \

v: vi
