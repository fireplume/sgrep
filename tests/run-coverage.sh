#!/usr/bin/env bash

export PYTHONPATH=$(pwd)/../sgrep

coverage run 	test_buffers.py
coverage run -a test_sgrep.py
coverage run -a parser_output_tst.py
if [[ $? -ne 0 ]]; then
  echo
  echo "!!! parser_output_tst failed !!!"
  echo
  exit 1
fi
coverage html --include='*/sgrep/sgrep.py,*/sgrep/Sgrep.py,*/sgrep/StackedBuffers.py'
firefox htmlcov/index.html
