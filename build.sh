#!/bin/sh

rm -rf build/ && python3 setup.py sdist -d build
twine upload --repository-url http://192.168.77.59:8888 dist/*
