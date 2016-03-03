#!usr/bin/bash

FUNC_REPO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/findmygits"
cd $FUNC_REPO
#echo $FUNC_REPO
. bin/activate
python findmygits.py