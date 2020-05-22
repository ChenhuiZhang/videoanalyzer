# Fetch the version from R0.1.0 to 0.1.0
PROG_VER=$(shell git describe --tags --abbrev=0 | cut -b 2-6)

build: clean version
	python3 setup.py sdist bdist_wheel -d build

release: build
	twine upload --repository-url http://192.168.77.59:8888 dist/*

clean:
	rm -rf build/ dist/

version:
	@sed -e 's/version=".*"/version="$(PROG_VER)"/' -i setup.py

