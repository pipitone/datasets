datasets
========

A tool to manage datasets on a shared filesystem. 

'datasets' is designed to make it easy for users of a shared filesystem to find
shared datasets and make lightweight (symlinked) copies of datasets to use in
personal analyses. 'datasets' also tries to keep track of data provenance and
encourage documentation. 

## Installation

```bash
$ git clone https://github.com/pipitone/datasets.git
$ cd datasets
$ ./setup.py     # must have virtualenv installed
```

Activate using `source env/bin/activate`, and deactivate using `source
env/bin/deactivate'. 

After running the setup script, you should be able to play around with sample
data: 

```bash
$ datasets list
- US_crime            Sample US crime data          

$ datasets copy US_crime
$ ls -l US_crime
total 4.0K
lrwxrwxrwx 1 jp jp  57 Mar 30 11:39 CrimeStatebyState.csv -> /home/jp/prj/datasets/test/US_crime/CrimeStatebyState.csv
lrwxrwxrwx 1 jp jp  48 Mar 30 11:39 fec96_10.csv -> /home/jp/prj/datasets/test/US_crime/fec96_10.csv
lrwxrwxrwx 1 jp jp  53 Mar 30 11:39 fec_codebook.txt: -> /home/jp/prj/datasets/test/US_crime/fec_codebook.txt:
-rw-r--r-- 1 jp jp 139 Mar 30 11:39 README
```
    


