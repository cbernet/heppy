# Heppy: Parallel Processing

Table of Contents:

  * [Heppy: Parallel Processing](#heppy-parallel-processing)
    * [Warning](#warning)
    * [Defining the number of jobs and dealing with the output](#defining-the-number-of-jobs-and-dealing-with-the-output)
    * [Local multiprocessing with heppy](#local-multiprocessing-with-heppy)
    * [Batch multiprocessing with heppy\_batch\.py](#batch-multiprocessing-with-heppy_batchpy)
      * [Submission](#submission)
      * [Resubmitting failed jobs](#resubmitting-failed-jobs)


## Warning 

Before attempting a massive processing of your events, you may want to:

* **make sure that your heppy configuration file is correct.** For example, load it in python, and make sure that your components are well defined. 
* **test your configuration file in heppy interactively.**

## Defining the number of jobs and dealing with the output

Typical physics analyses require the processing of millions of events coming from dozens of samples: data recorded during a given time period, Monte-Carlo signal sample, Monte-Carlo background samples, etc. 
In heppy, input samples may be declared in the following way: 

In `h_to_zz_samples.py`:

```python
import heppy.framework.config as cfg

data_period_A = cfg.DataComponent(
	'data_period_A',
	files=['A/file_1.root', 'A/file_2.root', ...]
)

data_period_B = cfg.DataComponent(
	'data_period_B',
	files=['B/file_1.root', 'B/file_2.root', ...]
)

ggH_125 = cfg.MCComponent(
	'ggH_125', 
	files=['ggH_125/file_1.root', 'ggH_125/file_2.root', ...]
)

ZZ = cfg.MCComponent(
	'ZZ', 
	files=['ZZ/file_1.root', 'ZZ/file_2.root', ...]
)
```

In the heppy configuration file `analysis_h_to_zz_cfg.py`: 

```python
from h_to_zz_samples import data_period_A, data_period_B, ggH_125, ZZ
selectedComponents = [data_period_A, data_period_B, ggH_125, ZZ]
```

Here, the list of files for each sample is written by hand but practically, the list of files for a given component is usually retrieved from a database or from the contents of a given directory.

When several components are selected, heppy starts a job for each component, and the output directory contains one subdirectory per component. All component subdirectories have the same structure, e.g.

```
Outdir/ 
	data_period_A/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt
	data_period_B/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt
	ggH_125/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt
	ZZ/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt	
```

It is often necessary to split the processing of a component in several jobs, by setting:

```python
# to get 10 jobs
component.splitFactor = 10
# or, to get one job per input file in this component
component.splitFactor = len(component.files)
```

If a component is split, each job will write to a specific _chunk_ directory: 

```
Outdir/
	ggH_125_Chunk1/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt	
	ggH_125_Chunk2/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt
	...	
```	

After the processing, bad chunks can be identified with `heppy_check.py`: 

```
heppy_check.py Outdir/*Chunk*
```

If some of the chunks are bad, you will need to resubmit them as explained below. If all of them are good you can add them: 

```
heppy_hadd.py Outdir/ 
```

to merge all chunks for each component. In this process, the root files are added with `hadd`, and the cut flow printouts added properly. 

```
Outdir/
	ggH_125/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt		
	ggH_125_Chunk1/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt	
	ggH_125_Chunk2/
		log.txt
		analyzer1/out_events.root
		analyzer2/cutflow.txt
	...	
```	

And you may remove the `Chunk*` directories from `Outdir`

## Local multiprocessing with `heppy`

Simply run `heppy` in the usual way after defining the number of jobs:

```heppy Outdir analysis_h_to zz.py``` 

When several components are selected, or when a component is split, heppy will start a separate thread on the local machine for each job. 

## Batch multiprocessing with `heppy_batch.py`

### Submission 

The `heppy_batch.py` script starts a separate process for each job.

To submit jobs on the 1nh queue of lsf: 

```
heppy_batch.py -o Outdir analysis_h_to zz.py -b 'bsub -q 1nh < batchScript.sh'
```

To submit jobs on the local machine with nohup:

```
heppy_batch.py -o Outdir analysis_h_to zz.py -b 'nohup ./batchScript.sh &'
```

For more information, ```heppy_batch.py -h```

### Resubmitting failed jobs

Go to the output directory of the failed job. This directory should contain a job script called `batchScript.sh`.
You can submit this job script directly to LSF or to your local machine:  

```
bsub -q 1nh < batchScript.sh
```

or 

```
nohup ./batchScript.sh &
```

Alternatively, if you want to resubmit all failed jobs on the batch queue, do something like:

```
heppy_check.py Outdir/*Chunk* -b 'bsub -q 1nh'
```
