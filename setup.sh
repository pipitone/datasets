#!/bin/bash
set -e

virtualenv env
. env/bin/activate
pip install pyyaml docopt
cat <<'EOF' > env/bin/datasets
#!/bin/bash

source $(dirname $0)/activate
python $(dirname $0)/../../datasets.py "$@"
EOF 

echo Fetching sample data...
mkdir -p test/US_crime
echo -e "---\ndataset: true\ndescription: Sample US crime data\n---\n" > test/US_crime/README
echo -e "---\ndatasets:\n  - $PWD/test/US_crime\n" > datasets.yml
(cd test/US_crime; 
    curl -O http://hci.stanford.edu/jheer/workshop/data/crime/CrimeStatebyState.csv;
    curl -O http://hci.stanford.edu/jheer/workshop/data/fec/fec96_10.csv;
    curl -O http://hci.stanford.edu/jheer/workshop/data/fec/fec_codebook.txt:
    curl -O http://hci.stanford.edu/jheer/workshop/data/fec/fec96_10.csv)

cat <<EOF

---
'datasets' has been been installed. To activate, run: 
    source env/bin/activate

Then run 'datasets list' to see installed datasets, or run 'datasets --help'
for more information on how to use this tool.
EOF
