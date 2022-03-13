.PHONY: compile-requirements
run:
	python app/main.py

.PHONY: compile-requirements
compile-requirements:
	pip-compile requirements.in
	pip-compile requirements-dev.in

.PHONY: sync-requirements
sync-requirements:
	pip-sync requirements.txt requirements-dev.txt

.PHONY: upgrade-requirements
upgrade-requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in