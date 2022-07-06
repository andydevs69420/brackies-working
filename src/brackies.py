from bparser import BrackiesMain
from bsymboltable import SymbolTable
from bvirtualmachine import BVirtualMachine


if __name__ == "__main__":

    brackie = BrackiesMain()

    fileptr = open("lib/sample.bruh", "r")
    abstree = brackie.parse(fileptr.name, fileptr.read())
    for node in abstree:
        node.compile()
    
    BVirtualMachine.run()