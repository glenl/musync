requirements:
	pip install -r requirements.txt

test:
	python -m unittest -v

coverage:
	coverage run -m unittest && \
	coverage html &&            \
	coverage report

install:
	python setup.py install

# preferred during development. See also: install
dev_install:
	pip install --editable .

dist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

.PHONY: requirements test coverage
.PHONY: install dev_install dist wheel
