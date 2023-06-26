all:
	@echo 'Try: make vi'

vi:
	vim \
		Makefile \
		README.md \
		bard-prompt \
		bard-prompt.py \
		bard-log \
		bard-log.py \
		settings.py \
		common.py \

v: vi
