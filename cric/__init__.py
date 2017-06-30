from __future__ import print_function
import glob
import sys
import yaml
from yaml import CLoader as Loader

import inning as inn
import match
import pickers as pic
import wrappers


def match_summaries_from_dir(fs_dir):
    files = glob.glob(fs_dir+'/*.yaml')
    num_files = len(files)
    for i, fname in enumerate(files):
        with open(fname, 'rb') as f:
            summary = yaml.load(f, Loader=Loader)
            print("Read file %s of %s" % (i+1, num_files), end='\r')
            sys.stdout.flush()
            yield summary
