Heppy : a python framework for high-energy physics data analysis
================================================================

Heppy (High Energy Physics with PYthon) is a modular python framework for the analysis of collision events.

If you're not very familiar with python yet, you will probably find the [Python Tutorial](https://docs.python.org/2.7/tutorial/) useful before you get started with heppy.

Table of contents:
master
1. [Installation](doc/Heppy_-_Installation_Instructions.md)
1. [Introduction](doc/Heppy_-_Introduction.md)
1. [A very simple example](doc/Heppy_-_a_very_simple_example.md)
1. [Parallel processing: running jobs](doc/Heppy_-_Parallel_Processing.md)
1. [Full analysis workflows](doc/Heppy_-_Full_analysis_workflows.md)
1. [Reference guide](http://fcc-support-heppy.web.cern.ch/fcc-support-heppy/)
1. [Generic analyses: working in several experiments](doc/particles.md)
1. [Papas, the parametrized particle simulation](doc/papas_-_The_PArametrized_PArticle_Simulation.md)

Support & feedback: [https://github.com/cbernet]()

New CONDOR batch :
-----------------
submit example :
heppy_batch.py -o Outdir FCChhAnalyses/FCChh/tttt/analysis.py -b 'run_condor.sh --bulk Outdir -f microcentury' --nevent 1000
-> in this example, CONDOR will look at all directories (could be Chunk too) in Outdir (--bulk Outdir) and run jobs for all of them into a single job. For example here, 10 jobs are coming from FCChhAnalyses/FCChh/tttt/analysis.py. And each job wii be run on 1000 evenmts.

[djamin@lxplus037 heppy]$ condor_q


-- Schedd: bigbird09.cern.ch : <188.185.71.142:9618?... @ 03/05/19 15:13:52
OWNER  BATCH_NAME        SUBMITTED   DONE   RUN    IDLE  TOTAL JOB_IDS
djamin CMD: batchScri   3/5  15:05      4      6      _     10 594302.1-9


run_condor.sh has been added in the new script/ directory

Instead of flavour (-f), it is possible to use maxruntime (unit = minute) : -t 60

Predefined timing jobs are done from flavour :
 20 mins -> espresso
 1h -> microcentury
 2h -> longlunch
 8h -> workday
 1d -> tomorrow
 3d -> testmatch
 1w -> nextweek

If job fails, can resubmit each failed job with :
heppy_check.py Outdir/*Chunk* -b 'run_condor.sh -f microcentury'

FCC actually have their own quota. To use it, you need to get yourself added to the egroup:
 
fcc-experiments-comp
 
Then you can add the following to your submit file:
 
+AccountingGroup = "group_u_FCC.local_gen"
