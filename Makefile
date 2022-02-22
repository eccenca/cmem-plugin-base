DOCKER_IMAGE = docker-registry.eccenca.com/eccenca-python:v3.5.0
DOCKER_RUN_PLAIN = docker run -i --workdir /data --rm -v $(shell pwd):/data ${DOCKER_IMAGE}
ARTIFACTS_DIR = artifacts
VERSION = $(shell git describe --always --dirty)
MY_PACKAGE = cmem_plugin_base
VERSION_FILE = ${MY_PACKAGE}/version.py

check-linters-local: check-safety-local check-pylint-local check-bandit-local check-mypy-local check-flake8-local

check-linters:
	${DOCKER_RUN_PLAIN} bash -c "make check-linters-local"


## create version.py for build
patch-version:
	@echo "------> TARGET: patch-version"
	echo "VERSION = '${VERSION}'" > ${VERSION_FILE}

# inject version on build
before-build: patch-version
