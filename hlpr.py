#
# Helper routines
# HanishKVC, 2021
#


import re


gDEBUGLVLERROR = 0
gDEBUGLVLWARN = 1
gDEBUGLVLINFO = 2
gDEBUGLVLTHRESHOLD = gDEBUGLVLWARN
gDEBUGLVLDEFAULT = gDEBUGLVLTHRESHOLD+1

DELIMITER = ','
FIELDPROTECTORS = [ "'", '"' ]


def dprint(msg, dbgLvl=None):
    dbgLvl = gDEBUGLVLDEFAULT if (dbgLvl == None) else dbgLvl
    if (dbgLvl > gDEBUGLVLTHRESHOLD):
        return
    print(msg)


def csv2list(inL, delim=DELIMITER, fieldProtectors = FIELDPROTECTORS):
    """
    Convert a csv line into a python list.
    delim: the character used to delimit the fields
    fieldProtectors: characters that could be used to protect fields having delim char in them.
    """
    tA = []
    curToken = ""
    bProtectedToken = False
    inL = inL.strip()
    if not inL.endswith(delim):
        inL += delim
    for c in inL:
        if (not bProtectedToken) and (c == delim):
            tA.append(curToken)
            curToken = ""
            continue
        if c in fieldProtectors:
            bProtectedToken = not bProtectedToken
            continue
        curToken += c
    return tA


SymbolMap = {
        'SEARCH55AA': 'REPLACEAA55'
        }


def symbolmap_append(inMap):
    global SymbolMap
    for k in inMap:
        SymbolMap[k] = inMap[k]


def fix_symbol(symbol):
    symSuffix = symbol[-3:]
    if symSuffix in [ "-BE", "-BZ" ]:
        symbol = symbol[:-3]
    if symbol in SymbolMap:
        symbol = SymbolMap[symbol]
    return symbol


def print_dict(d, msg=None):
    if msg:
        print(msg)
    for k in d:
        print("{}:\n\t{}".format(k,d[k]))


def match_any(matchList, theStr):
    for cM in matchList:
        if re.match(cM, theStr) != None:
            return True
    return False


