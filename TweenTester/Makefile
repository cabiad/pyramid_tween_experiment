VIRTUALENV = virtualenv

INSTALL = bin/pip install
INSTALLOPTIONS = -U

SYSTEM_PYTHON = /usr/bin/python
PIP = bin/pip
PYTHON = bin/python
PSERVE = bin/pserve

###########################
# Targets                 #
###########################
.PHONY: bootstrap

bootstrap:
	@$(VIRTUALENV) -p $(SYSTEM_PYTHON) --distribute .
	@$(INSTALL) -r requirements/dev.txt
	@$(PYTHON) setup.py develop
	@bin/initialize_TweenTester_db development.ini

.PHONY: rundev
rundev:
	@$(PSERVE) development.ini
