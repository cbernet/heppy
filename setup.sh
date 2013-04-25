#!env bash

source external/root/bin/thisroot.sh
export TLEP=$PWD
export PYTHONPATH=$.:$TLEP/external/tables-2.4.0:$TLEP:$PYTHONPATH
