import argparse
from os import path
from os import curdir
from berrhandler import errorHandler, errorType

argparser = argparse.ArgumentParser()
argparser.add_argument("-f", metavar="--file", nargs = 1, help="Input file to run", type=str)
arguments = argparser.parse_args()

__FILE_INPUT__ = arguments.f
__FILEFORMAT__ = ".bruh"

if  __FILE_INPUT__ == None:
    errorHandler.throw__error(
        errorType.BRACKIES_ERROR, "input file is not defined!!!"
    )

if  not path.isfile(__FILE_INPUT__[0]):
    errorHandler.throw__error(
        errorType.BRACKIES_ERROR, "\"" + __FILE_INPUT__[0] + "\" is not a file!!!"
    )

if  not __FILE_INPUT__[0].endswith(__FILEFORMAT__):
    errorHandler.throw__error(
        errorType.BRACKIES_ERROR, "invalid file \"" + __FILE_INPUT__[0] + "\"!!!"
    )

from bparser import BrackiesMain
from bsymboltable import SymbolTable
from bvirtualmachine import BVirtualMachine


if __name__ == "__main__":

    brackie = BrackiesMain()

    fileptr = open(__FILE_INPUT__[0], "r")
    abstree = brackie.parse(fileptr.name, fileptr.read())
    for node in abstree:
        node.compile()
    
    BVirtualMachine.run()