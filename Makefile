.DEFAULT_GOAL := help
.PHONY: coverage deps help lint publish push test tox requirements venv

VER=$(shell git log --pretty=format:'%h' -n 1)

create_service: ##Create service from docker image
	docker service create --name loudify-worker martynvandijke/loudify-worker:dev

compile_runner:
	nuitka3 --follow-imports apps/cran_send.py

compile_runner:
	nuitka3 --follow-imports apps/runner.py

build_image: compile_runner ##Build docker image
	docker build -t martynvandijke/loudify-worker:dev .
	docker push martynvandijke/loudify-worker:dev

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
