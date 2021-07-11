#!/usr/bin/env python3
# Store Assets data
# HanishKVC, 2021
# GPL


import sys
import os
import time
import numpy
import readline
import rlcompleter
import traceback

from hlpr import *
import csv
import generic
import kite
import h7
import adb


HISTORYFILE="./.assetsdb.history"


def startup_message():
    print("INFO: AssetsDB")
    print("NOTE: exit() to quit")


def startup():
    csv.init()
    readline.parse_and_bind("tab: complete")
    startup_message()


def load_history(histFile):
    if os.path.exists(histFile):
        readline.read_history_file(histFile)
    else:
        f = open(histFile, mode="wt")
        f.close()


def save_history(histFile):
    readline.write_history_file(histFile)


def init_scripts(srcFiles):
    for srcFile in srcFiles:
        f = open(srcFile)
        src = f.read()
        f.close()
        exec(src, globals())


def _runme():
    while True:
        try:
            bDoExec = False
            try:
                toRun = ""
                thePrompt = "$"
                while True:
                    got = input(thePrompt)
                    thePrompt = " "
                    if (got != ""):
                        if (got[-1] != "\\"):
                            toRun += got
                            break
                        else:
                            toRun += (got[:-1] + "\n")
                    else:
                        break
                res = eval(toRun)
            except SyntaxError:
                bDoExec = True
            if bDoExec:
                res = exec(toRun)
            if(type(res) != type(None)):
                print(res)
        except:
            if (sys.exc_info()[0] == SystemExit):
                break;
            #print("ERRR:", sys.exc_info())
            traceback.print_exc()


def runme():
    init_scripts(sys.argv[1:])
    load_history(HISTORYFILE)
    _runme()
    save_history(HISTORYFILE)


startup()
runme()

