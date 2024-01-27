run:
	@python3 encoding/cli.py --daemon

watch:
	@find /app/encoding -name *.py |entr -r python encoding/cli.py --daemon
