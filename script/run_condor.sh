#!/bin/bash

if [[ "$1" == "--help" || "$1" == "-h"  || "$1" == "-?" ]]; then
    echo "usage: $0 [ -f flavour | -t max_runtime_in_minutes ] script.sh "
    exit 1;
fi

bulk=""
if [[ "$1" == "--bulk" ]]; then
    bulk=$2; shift; shift;
fi

flavour=""
if [[ "$1" == "-f" && "$2" != "" ]]; then
    flavour=$2;
    shift; shift
fi
maxruntime="-t" # time in minutes
if [[ "$1" == "-t" && "$2" != "" ]]; then
    if [[ "${flavour}" != "" ]]; then 
        echo "Can't set both flavour and maxruntime"; 
        exit 1; 
    fi;
    maxruntime=$(( $2 * 60 ));
    shift; shift
fi

here=$(pwd)
if [[ "$bulk" != "" ]]; then
    jobdesc="jobs_desc_${bulk}.cfg"
    prefix="\$(Chunk)/";
    here="$here/\$(Chunk)"
else
    jobdesc="job_desc.cfg"
    prefix=""
fi;

scriptName=${1:-./batchScript.sh}

# SLCern6 -> CentOS7 when ready
# requirements:  (Machine =!= LastRemoteHost) 
cat > $jobdesc <<EOF
Executable     = ${prefix}${scriptName}
Log            = ${prefix}condor_job_\$(ProcId).log
Output         = ${prefix}condor_job_\$(ProcId).out
Error          = ${prefix}condor_job_\$(ProcId).error
getenv         = True
environment    = "LS_SUBCWD=${here}"
request_memory = 2G
requirements   = ( (OpSysAndVer =?= "CentOS7") 
on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)
max_retries    = 3
+AccountingGroup = "group_u_FCC.local_gen"
EOF

[[ "${flavour}" != "" ]] && echo "+JobFlavour = \"${flavour}\"" >> $jobdesc
[[ "${maxruntime}" != "" ]] && [[ "${maxruntime}" != "-t" ]] && echo "+MaxRuntime = ${maxruntime}" >> $jobdesc

if [[ "$bulk" != "" ]]; then
    echo "queue Chunk matching dirs ${bulk}/*_Chunk*" >> $jobdesc
else
    echo "queue 1" >> $jobdesc
fi;

# Submit job
/usr/bin/condor_submit $jobdesc
