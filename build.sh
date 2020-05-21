#!/bin/sh

rm -rf build/ dist/ && python3 setup.py sdist bdist_wheel -d build
twine upload --repository-url http://192.168.77.59:8888 dist/*
