#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import yaml
import datetime
import os.path
import exceptions

from functools import wraps
from docopt import docopt


__version__ = '0.1.0'

defaultconfigs = [ os.path.join(sys.path[0],'datasets.yml'),
                '/etc/datasets.yml',
                os.path.expanduser('~/.datasets.yml'),
                './datasets.yml' ]

class Dataset:
    """Represents a dataset"""
    def __init__(self, path, basedir = None):
        self.basedir = basedir or os.path.dirname(path)
        self.path = path
        self._info()

    def _info(self):
        readme = os.path.join(self.path,'README')
        if not os.path.isfile(readme):
            raise InvalidDatasetException(
                'Invalid dataset %s. Does not contain a README file.'%self.path)
        
        self.name = os.path.relpath(self.path, self.basedir)
        doc = yaml_safe_load_first(open(readme))
        if not doc.get('dataset'):
            raise InvalidDatasetException(
                "Invalid dataset %s. Expected README YAML frontmatter to have 'dataset: true'." % self.path)
        self.description = doc.get('description', "")

    def get_subdatasets(self):
        sub = []
        subfiles = [os.path.join(self.path, i) for i in os.listdir(self.path)]
        for d in [i for i in subfiles if os.path.isdir(i)]:
            try:
                sub.append(Dataset(d, basedir=self.basedir))
            except (InvalidDatasetException):
                pass
        return sub

class InvalidDatasetException(exceptions.Exception):
    pass

def argparsed(func):
    @wraps(func)
    def wrapped(argv, config):
        args = docopt(func.__doc__, argv=argv)
        return func(args, config)
    return wrapped

def load_configs(configs):
    paths = set()
    for i in [f for f in configs if os.path.isfile(f)]:
        for y in yaml.safe_load_all(open(i)):
            paths.update(set(y.get('datasets',[])))
            break;          # only read the first YAML document per file
    datasets = []
    for i in paths:
        try:
            datasets.append(Dataset(i))
        except (InvalidDatasetException):
            pass # TODO: verbose warning
    return {"datasets":datasets}

def get_dataset(path, roots):
    if path.startswith('/'):
        return Dataset(path)
    head = path.split('/')[0]
    for root in roots:
        if head == os.path.basename(root.path):
            return Dataset(os.path.join(os.path.dirname(root.path),path))
    raise InvalidDatasetException("%s is not a dataset" % path)

@argparsed
def list(args, config):
    """
Usage: datasets list [options] [<dataset>...]

Show a short description for each of the available <dataset>s.

Options:
    <dataset>           Dataset name.
    -r --recursive      List all subdatasets.
    --verbose           Include more detailed descriptions if available.

Notes: 
    A dataset is simply a folder that has a README file that begins with: 

        ---
        dataset: true
        description: optionally, a description here
        ---

    You can register datasets by creating a file in ~/.datasets.yml, or
    ./datasets.yml that starts with the following: 

        ---
        datasets: 
            # just include the path to the dataset folder 
            # NOTE: folder must include a README 
            - /data/all_nsa_data/
            - /data/mitt_romney_taxes/

"""
    def _print_dataset(ds, args):
        print " - {:<30}     {:<30}".format(ds.name, ds.description)
        if args["--verbose"]:
            print "   {:<30}     Location: {:<30}".format("", ds.path)
        if args["--recursive"]:
            for i in ds.get_subdatasets():
                _print_dataset(i, args)

    if not config["datasets"]:
        print "No datasets found."
        return

    sets = config['datasets']
    if args['<dataset>']:
        args['--recursive'] = True
        try:
            sets = map(lambda x: get_dataset(x, sets), args['<dataset>'])
        except InvalidDatasetException, e:
            print >> sys.stderr, "ERROR: %s" % e
            sys.exit(-1)

    print "Datasets:"
    for ds in sets:
        _print_dataset(ds, args)
    print

@argparsed
def copy(args, config):
    """
Usage: datasets copy[options] <dataset>...

Make a lightweight copy of a <dataset>.

Options:
    <dataset>           Dataset Name
    -c, --clobber       Clobber existing files [Default: False]
    -n, --dry-run       Show what would happen.
"""
    if not config["datasets"]:
        print "No datasets found."
        return
  
    try:
        sets = map(lambda x: get_dataset(x, config['datasets']), args['<dataset>'])
    except InvalidDatasetException, e:
        print >> sys.stderr, "ERROR: %s" % e
        sys.exit(-1)

    for ds in sets:
        rootdir = ds.name
        os.mkdir(rootdir) 
        for (path, dirs, files) in os.walk(ds.path):
            relpath = os.path.relpath(path,ds.path)
            for f in files: 
                source = os.path.realpath(os.path.join(ds.path,path,f))
                target = os.path.join(rootdir,relpath,f)
                if relpath == "." and f == 'README': 
                    frontmatter, rest = get_readme(source)
                    frontmatter['source'] = ds.path
                    frontmatter['datecopied'] = datetime.datetime.now()
                    t = open(target, "w")
                    t.write(yaml.dump(frontmatter,
                        explicit_start = True, default_flow_style = False))
                    t.write('---\n')
                    t.write(rest)
                    t.close()
                else: 
                    os.symlink(source, target)
            for d in dirs:
                os.mkdir(os.path.join(rootdir,relpath,d))

@argparsed
def create(args, config): 
    """
A dataset itself is simply any folder with specially formatted README file in
it. The README file must start with the following:

    ---
    dataset: true
    description: A short one-liner description of the dataset
    includes:
        - folder1
        - folder2
    ---

And may be followed by anything else.
"""
    pass

def get_readme(path): 
    """returns (yamldoc, rest)"""
    content = open(path).read()
    match = re.match( r'^(---\s*$.*?^---\s*$)(.*)', content, re.MULTILINE | re.DOTALL )
    return (yaml_safe_load_first(match.group(1)), match.group(2))

def yaml_safe_load_first(content):
    for i in yaml.safe_load_all(content):
        return i
    
def main(argv = None):
    """datasets is a simple utility for discovering datasets and making lightweight
copies to use in analyses. 

Usage:
    datasets <command> [<options>...]

General Options:
    -h, --help       Show help.
    --version        Show version and exit.

Commands:
    list             List available datasets.
    copy             Get a lightweight copy of a dataset.
    create           Create an empty dataset.
    register         Register a dataset in ~/.datasets.yml.
    bash_completion  Add bash autocomplete code to your ~/.bashrc

See 'datasets help <command>' for more information on a specific command."""

    args = docopt(main.__doc__,
                  version='datasets version %s' % __version__,
                  options_first=True,
                  argv=argv or sys.argv[1:])

    cmd = args['<command>']
    try:
        method = globals()[cmd]
        assert callable(method)
    except (KeyError, AssertionError):
        exit("%r is not a datasets command. See 'datasets help'." % cmd)

    config = load_configs(defaultconfigs)

    argv = [args['<command>']] + args['<options>']
    return method(argv, config)

if __name__ == '__main__':
    main()





