#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place line_provider --exclude=__init__.py
black line_provider
isort --recursive --apply line_provider
