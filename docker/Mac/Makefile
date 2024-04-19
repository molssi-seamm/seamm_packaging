.PHONY: help zip
.DEFAULT_GOAL := zip

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef

export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

zip: ## Create the zip files for the documentation
	zip -9 -r ../../../molssi-seamm.github.io/docs/getting_started/installation/SEAMM SEAMM.app/
	zip -9 -r ../../../molssi-seamm.github.io/docs/getting_started/installation/Dashboard Dashboard.app/

