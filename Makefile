.PHONY: vsetup
vsetup:
	test -d venv || virtualenv venv

.PHONY: clean
clean: clean-build clean-pyc clean-test
	rm -rvf ./*.tgz ./venv ./protobufs ./*.log ./*.xml

## Remove Python build artifacts
.PHONY: clean-build
clean-build:
	rm -vrf ./build/
	rm -vrf ./dist/
	rm -vrf ./.eggs/
	rm -vrf ./*.egg-info

## Remove Python file artifacts and binaries
.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -delete -print
	find . -name '*.pyo' -delete -print
	find . -name '*~' -delete -print
	find . -name '__pycache__' -delete -print

## Remove Python test and Code coverage artifacts
.PHONY: clean-test
clean-test:
	rm -vrf .tox/
	rm -f .coverage
	rm -vrf htmlcov/
	rm -vrf ./tests/.cache
	rm -vrf .pytest_cache

.PHONY: distclean
distclean:
	git clean -fdX

