setup: # Run first time when pull the repo
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install
	pre-commit install --hook-type commit-msg
	pre-commit autoupdate

check_precommit: # Check all files with pre-commit
	pre-commit run --all-files
