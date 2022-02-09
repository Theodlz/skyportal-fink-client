SHELL = /bin/bash

BOLD=\033[1m
NORMAL=\033[0m

VER := $(shell cd skyportal && python -c "import skyportal; print(skyportal.__version__)")
BANNER := $(shell echo -e "Welcome to $(BOLD)SkyPortal Contrib v$(VER)$(NORMAL) (https://skyportal.io)")

$(info $())
$(info $(BANNER))
$(info $())

help: skyportal/baselayer/Makefile
	@echo -e "  To $(BOLD)start developing$(NORMAL) the web application, do \`make dev\`."
	@echo
	@echo Please choose one of the following make targets:
	@python skyportal/baselayer/tools/makefile_to_help.py "Web Server":skyportal/baselayer/Makefile "SkyPortal-specific":skyportal/Makefile
	@echo

skyportal/baselayer/Makefile:
	git submodule update --init

dev: docker-up
	@python ./util/sp_tokens.py --container_name skyportal_web_1  --verbose=False

dev-down: 
	docker-compose --file=skyportal/docker-compose.yaml down

docker-up: docker-local
	docker-compose --file=skyportal/docker-compose.yaml up -d

docker-local: ## Build docker images locally
	cd skyportal && git submodule update --init --remote
	cd skyportal && docker build -t skyportal/web .

docs: ## Build the SkyPortal docs
docs: | doc_reqs api-docs
	export SPHINXOPTS=-W; make -C doc html

# Lint targets
lint-install: ## Install ESLint and a git pre-commit hook.
lint-install: cp-lint-yaml lint-githook
		@echo "Installing latest version of ESLint and AirBNB style rules"
		@./skyportal/baselayer/tools/update_eslint.sh

cp-lint-yaml: ## Copy eslint config file to parent app if not present
		@if ! [ -e .eslintrc.yaml ]; then \
			echo "No ESLint configuration found; copying baselayer's version of .eslintrc.yaml"; \
			cp skyportal/baselayer/.eslintrc.yaml .eslintrc.yaml; \
		fi

$(ESLINT): lint-install

lint: ## Check JavaScript code style.
		$(ESLINT) --ext .jsx,.js -c .eslintrc.yaml static/js

lint-unix:
		$(ESLINT) --ext .jsx,.js -c .eslintrc.yaml --format=unix static/js

lint-githook:
		@if ! [ -e .git/hooks/pre-commit ]; then \
			echo "Installing ESLint pre-commit hook into \`.git/hooks/pre-commit\`"; \
			cp skyportal/baselayer/.git-pre-commit .git/hooks/pre-commit; \
		fi

# https://www.gnu.org/software/make/manual/html_node/Overriding-Makefiles.html
%: skyportal/baselayer/Makefile force
	@$(MAKE) --no-print-directory -C . -f skyportal/baselayer/Makefile $@

.PHONY: Makefile force
