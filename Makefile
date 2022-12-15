.PHONY: clean
clean:
	find . -name '*.pyo' -delete
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	find . -name '*~' -delete
	find . -name '.coverage.*' -delete

.PHONY: entry-point-test
entry-point-test:
	cd ~ && python -c "from autonormalize import autonormalize"

.PHONY: lint
lint:
	isort --check-only autonormalize
	black autonormalize docs/source -t py311 --check
	flake8 autonormalize

.PHONY: lint-fix
lint-fix:
	black autonormalize docs/source -t py311
	isort autonormalize

.PHONY: test
test:
	pytest autonormalize/ -n auto

.PHONY: testcoverage
testcoverage:
	pytest autonormalize/ -n auto --cov=autonormalize

.PHONY: installdeps
installdeps: upgradepip
	pip install --upgrade pip
	pip install -e ".[dev]"

.PHONY: upgradepip
upgradepip:
	python -m pip install --upgrade pip

.PHONY: upgradebuild
upgradebuild:
	python -m pip install --upgrade build

.PHONY: upgradesetuptools
upgradesetuptools:
	python -m pip install --upgrade setuptools

.PHONY: package
package: upgradepip upgradebuild upgradesetuptools
	python -m build
	$(eval PACKAGE=$(shell python -c "from pep517.meta import load; metadata = load('.'); print(metadata.version)"))
	tar -zxvf "dist/autonormalize-${PACKAGE}.tar.gz"
	mv "autonormalize-${PACKAGE}" unpacked_sdist
