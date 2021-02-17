.PHONY: entry-point-test
entry-point-test:
	cd ~ && python -c "from featuretools import autonormalize"

.PHONY: lint-fix
lint-fix:
	select="E225,E303,E302,E203,E128,E231,E251,E271,E127,E126,E301,W291,W293,E226,E306,E221"
	autopep8 --in-place --recursive --max-line-length=100 --select=${select} autonormalize
	isort --recursive autonormalize

.PHONY: lint
lint:
	flake8 autonormalize
	isort --check-only --recursive autonormalize

.PHONY: lint_tests
lint_tests:
	flake8 autonormalize
	isort --check-only --recursive autonormalize

.PHONY: test
test: lint
		pytest autonormalize/

.PHONY: testcoverage
testcoverage: lint
		pytest autonormalize/ --cov=autonormalize

.PHONY: unit_tests
unit_tests:
	pytest --cache-clear --show-capture=stderr -vv ${addopts}

.PHONY: package_build
package_build:
	rm -rf dist/package
	python setup.py sdist
	$(eval package=$(shell python setup.py --fullname))
	tar -zxvf "dist/${package}.tar.gz" 
	mv ${package} dist/package
