from core.bobject import Obj


class Frame(object):
    def __init__(self, _instructions):
        self.__locals:list[Obj] = []
    
    def putLocal(self, _obj:Obj):
        self.__locals.append(_obj)
    
    def getLocal(self, _idx:int):
        return self.__locals[_idx]


class VirtualMachine:
    
    STACK_FRAME:list[Frame] = []
    ###############
    HEAP_MEMORY:Obj = []
    EVAL_STACKS:Obj = []

    @staticmethod
    def allocate():
        VirtualMachine.HEAP_MEMORY.append(None)
        return (len(VirtualMachine.HEAP_MEMORY) - 1)

    @staticmethod
    def run():
        ...
    