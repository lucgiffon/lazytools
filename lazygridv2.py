#!/usr/bin/env python3

"""
The lazygrid program allows to build command lines array from a configuration file.

Command line arrays are text files containing one set of command line arguments at each line.

This is usefull for grid search: you can launch the same script many times with different arguments stored in the command line array.


How does this work?
-------------------

You can find an example of configuration file just beside this script: `lazyfile_example.yml`. There is also an example output of such configuration file in `arrayparam_example.txt`.
Just like Makefiles, the lazyfile is structured by rules that rely upon each other.

The rule `all` is the master rule of the file, this is the one that will be executed and its absence will result in an error. The rule `all` calls
other rules. In contrary to other rules, the rule `all` will not concatenate the output of its subrule but simply launch them, one after the other.

A rule can have keyword parameters or simple parameters:

{"--this-is-a-kw-parameter": ["kw parameter can take one value", "or one other value"]}

["--this-is-a-simple-boolean-parameter", "--this-is-an-other-simple-boolean-parameter"]


Usage:
    lazygrid -l lazyfile

Options:
    -l --lazyfile lazyfile          The input configuration yml file.
"""

import yaml
from collections import OrderedDict
from pprint import pprint
import copy
import numpy as np
import math
import os
import time
import random

# todo specify external modules (ex numpy/maths) in the yaml file
from docopt import docopt
from pathlib import Path

LAZYFILENAME = None


def build_arguments_combinations_of_rule(rulename, rule_content, dct_current_argument_combinations_by_rule):
    cmd_line_case = [""]  # the initial argument combination is just the empty argument combination
    for key, value in rule_content.items():
        # each new item in the rule will be appended to all
        # the previously constructed argument combinations of the rule

        # value = eval(str(value))
        tmp_cmd_line_case = []

        # positional arguments are stored in a list
        if type(value) == list:
            for cmd in cmd_line_case:
                for elm in value:
                    tmp_cmd_line_case.append(" ".join([cmd, elm]).strip())

        # keyword arguments are stored in a dict, ordered because yaml keep the ordering
        elif type(value) == OrderedDict:
            # todo manage combinatory by using dict with more than 1 element
            for cmd in cmd_line_case:
                for key_arg, value_arg in value.items():
                    formated_value_arg = (f"" + str(value_arg)).format(LAZYFILE=LAZYFILENAME)
                    lst_value_arg = eval(str(formated_value_arg))
                    for value_arg in lst_value_arg:
                        tmp_cmd_line_case.append(" ".join([cmd, str(key_arg) + " " + str(value_arg)]).strip())

        # in case there is only
        elif type(value) == str:
            raise NotImplementedError("Sould make evaluation here")

        elif value is None:
            try:
                to_add_cmd_line = dct_current_argument_combinations_by_rule[key]
            except KeyError:
                raise KeyError(
                    "{} is referenced in {} but doesnt exist. Make sure it is defined BEFORE the section {}".format(key,
                                                                                                                    rulename,
                                                                                                                    rulename))

            for cmd in cmd_line_case:
                for cmd_line_to_add in to_add_cmd_line:
                    tmp_cmd_line_case.append(" ".join([cmd, cmd_line_to_add]))

        else:
            raise Exception

        # new argument combinations have been created from the previous ones, and now they replace them
        cmd_line_case = tmp_cmd_line_case

    return cmd_line_case


def build_cmd(dict_arg):
    cmd_lines = []
    try:
        todo_cmd_lines = dict_arg["all"].keys()
    except KeyError:
        raise KeyError("There should be a rule 'all'")

    assert list(dict_arg.keys())[0] == "all"

    dct_argument_combinations_by_rule = {}
    all_rule_names = list(dict_arg.keys())[1:]
    for rulename in all_rule_names:
        # for each rule, build the list of argument combinations which it describes
        rule_content = dict_arg[rulename]
        lst_arguments_combinations_for_rule = build_arguments_combinations_of_rule(rulename, rule_content, dct_argument_combinations_by_rule)
        dct_argument_combinations_by_rule[rulename] = lst_arguments_combinations_for_rule

    for todo_cmd_line in todo_cmd_lines:
        cmd_lines.extend(dct_argument_combinations_by_rule[todo_cmd_line])

    return cmd_lines


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def main():
    global LAZYFILENAME
    arguments = docopt(__doc__)
    abspath_lazyfile = os.path.abspath(arguments["--lazyfile"])
    LAZYFILENAME = "/".join(abspath_lazyfile.split("/")[-3:]).split(".")[0]
    with open(abspath_lazyfile) as f:
        dataMap = ordered_load(f)
    final_cmd_lines = build_cmd(dataMap)
    for line in final_cmd_lines:
        print(line)

if __name__ == "__main__":
    main()





