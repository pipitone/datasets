#!/bin/bash

virtualenv env
. env/bin/activate
pip install pyyaml docopt

echo "#!/bin/bash" > env/bin/datasets 
echo "python $PWD/datasets.py \"\$@\"" >> env/bin/datasets
chmod +x env/bin/datasets

cat <<EOF

---
'datasets' has been been installed. To activate, run: 
    source env/bin/activate

Then run 'datasets list' to see installed datasets, or run 'datasets --help'
for more information on how to use this tool.
EOF
