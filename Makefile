.PHONY: clean
clean:
	find . -name '*.pyo' -delete
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	find . -name '*~' -delete

.PHONY: entry-point-test
entry-point-test:
	cd ~ && python -c "from featuretools import autonormalize"

.PHONY: lint
lint:
	flake8 autonormalize && isort --check-only autonormalize

.PHONY: lint-fix
lint-fix:
	autopep8 --in-place --recursive --max-line-length=100 --exclude="*/migrations/*" --select="E225,E303,E302,E203,E128,E231,E251,E271,E127,E126,E301,W291,W293,E226,E306,E221,E261,E111,E114" autonormalize
	isort autonormalize

.PHONY: testcoverage
testcoverage: lint
		pytest autonormalize/ --cov=autonormalize

.PHONY: package_autonormalize
package_autonormalize:
	python setup.py sdist
	$(eval DT_VERSION=$(shell python setup.py --version))
	tar -zxvf "dist/autonormalize-${DT_VERSION}.tar.gz"
	mv "autonormalize-${DT_VERSION}" unpacked_sdist