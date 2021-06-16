#!/usr/bin/env python3
# Store Assets data
# HanishKVC, 2021
# GPL


import sys
import numpy


DELIMITER = ','


def csv2array(inL):
    tA = []
    curToken = ""
    bProtectedToken = False
    inL = inL.strip()
    if not inL.endswith(DELIMITER):
        inL += DELIMITER
    for c in inL:
        if (not bProtectedToken) and (c == DELIMITER):
            tA.append(curToken)
            curToken = ""
        if c in [ "'", '"' ]:
            bProtectedToken = not bProtectedToken
    return tA


def import_csv_o1(sFile):
    f = open(sFile)
    l.readline()
    for l in f:
        print(csv2array(l))


import_csv_o1(sys.argv[1])

