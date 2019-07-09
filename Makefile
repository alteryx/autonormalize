.PHONY: clean
clean:
	find . -name '*.pyo' -delete
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	find . -name '*~' -delete

.PHONY: lint
lint:
	flake8 autonormalize && isort --check-only --recursive autonormalize

.PHONY: lint-fix
lint-fix:
	autopep8 --in-place --recursive --max-line-length=100 --select="E225,E303,E302,E203,E128,E231,E251,E271,E127,E126,E301,W291,W293,E226,E306,E221" autonormalize
	isort --recursive autonormalize

.PHONY: test
test:
	pytest autonormalize/tests

.PHONY: testcoverage
testcoverage: lint
	pytest autonormalize/tests --cov=autonormalize

.PHONY: installdeps
installdeps:
	pip install --upgrade pip -q
	pip install -e . -q
	pip install -r dev-requirements.txt -q