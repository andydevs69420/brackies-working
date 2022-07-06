from unittest import result
from blogger import log__info
from core.bobject import *
from btoken import trace__token
from bsymboltable import SymbolTable
from core.bcore import println, typeCheck, evaluate
from bbytecode import OpCode, ByteCodeChunk
from berrhandler import errorHandler, errorType
class BVirtualMachine:pass


class StackFrame:
    MAX_FRAME_SIZE = 40000

    def __init__(self):
        self.__internal = []
        self.__has_new_frame = False
    
    def push(self, _instructions:tuple):
        if  len(self.__internal) + 1 > StackFrame.MAX_FRAME_SIZE:
            func = BVirtualMachine.NAMED_CALL_STACK[-1]
            func_prop = SymbolTable.lookup(func)
            _msg = ""
            _msg += "maximum recursion reached!, function \"" + func + "\" is called " + str(BVirtualMachine.CALL_COUNTER[func]) + " times."
            _msg += "\n"
            _msg += trace__token(func_prop["token"])

            return errorHandler.throw__error(errorType.STACK_OVERFLOW, _msg)

        self.__has_new_frame = True
        self.__internal.append(_instructions)

    def peek(self):
        if  self.isempty():
            return []
        self.__has_new_frame = False
        return self.__internal[-1]

    def pop(self):
        if  self.isempty():
            return []
        self.__has_new_frame = True
        return self.__internal.pop()

    def isempty(self):
        return len(self.__internal) <= 0
    
    def hasNewFrame(self):
        return self.__has_new_frame
 

class GarbageCollector:

    REFERENCE_COUNTER = {}

    @staticmethod
    def increment_count(_memory_index:int):
        if  _memory_index not in GarbageCollector.REFERENCE_COUNTER.keys():
            GarbageCollector.REFERENCE_COUNTER[_memory_index] = 1
        else:
            GarbageCollector.REFERENCE_COUNTER[_memory_index] += 1
        
    

class BVirtualMachine(GarbageCollector):


    ###### VIRTUAL MACHINE ######
    STACK_FRAME  = StackFrame()
    VIRT__HEAPM  = []
    EVAL__STACK  = []
    INSTRUCTIONS = []

    ######## NAMED CALL STACK ######
    SCOPE_STACK  = []
    CALL_COUNTER = {}
    NAMED_CALL_STACK = []

    ###### INSTRUCTION POINTER ######
    POINTER = 0
    CONTROLL_HISTORY = [0] # BVirtualMachine.POINTER DEFAULT := 0

    @staticmethod
    def push_instruction(_chunk:ByteCodeChunk):
        BVirtualMachine.INSTRUCTIONS.append(_chunk)

    @staticmethod
    def alloc_heap():
        BVirtualMachine.VIRT__HEAPM.append(0)
        return len(BVirtualMachine.VIRT__HEAPM) - 1
    
    @staticmethod
    def push_to_heap(_obj:object):
        BVirtualMachine.VIRT__HEAPM.append(_obj)
        return len(BVirtualMachine.VIRT__HEAPM) - 1
    
    @staticmethod
    def get_from_heap(_index:int):
        return BVirtualMachine.VIRT__HEAPM[_index]

    @staticmethod
    def push_frame(_frame:tuple or list):
        BVirtualMachine.STACK_FRAME.push(_frame)

    @staticmethod
    def execute_byte(_bytecode:ByteCodeChunk):
        _opcode = _bytecode.getOpcode()
        if  _opcode == OpCode.LOAD_BUILTINS:
            return load_builtins(_opcode)
        elif _opcode == OpCode.NO_OP:
            return # directly return
        elif  _opcode == OpCode.PUSH_CONST:
            return push_const(_bytecode)
        elif _opcode == OpCode.PUSH_NAME:
            return push_name(_bytecode)
        elif _opcode == OpCode.PUSH_ATTRIB:
            return push_attrib(_bytecode)
        elif _opcode == OpCode.STORE_FUNC:
            return store_func(_bytecode)
        elif _opcode == OpCode.STORE_NAME:
            return store_name(_bytecode)
        elif _opcode == OpCode.STORE_LOCAL:
            return store_local(_bytecode)
        elif _opcode == OpCode.BINARY_EXPR:
            return binary_expr(_bytecode)
        elif _opcode == OpCode.POP_TOP:
            return pop_top(_bytecode)
        elif _opcode == OpCode.CALL:
            return call_expr(_bytecode)
        elif _opcode == OpCode.RETURN:
            return return_opcode(_bytecode)
        else:
            for _code in BVirtualMachine.INSTRUCTIONS:
                print(_code.__str__())
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "not implemented opcode \"" + _opcode.name + "\"!"
            )

    @staticmethod
    def run():
        for _code in BVirtualMachine.INSTRUCTIONS:
            print(_code.__str__())

        BVirtualMachine.STACK_FRAME.push(BVirtualMachine.INSTRUCTIONS)

        while not BVirtualMachine.STACK_FRAME.isempty():
            current_frame = BVirtualMachine.STACK_FRAME.peek() 
            
            # log__info("##################################")
            # log__info("# EXECUTING AT: " + str(BVirtualMachine.POINTER * 2))
            # log__info("# EXECUTING AT: " + current_frame[BVirtualMachine.POINTER].__str__())
            # for each_byte in current_frame:
            #     log__info("# " + each_byte.__str__())
            # log__info("# --------------------------------")
            # BVirtualMachine.STACK_FRAME.pop()
            
            while BVirtualMachine.POINTER < len(current_frame):
                BVirtualMachine.execute_byte(current_frame[BVirtualMachine.POINTER])
                if BVirtualMachine.STACK_FRAME.isempty() or BVirtualMachine.STACK_FRAME.hasNewFrame():
                    break
                else:
                    BVirtualMachine.POINTER += 1
            
        log__info("Finished!")
        # for each_remaining in BVirtualMachine.EVAL__STACK:
        #     log__info(BVirtualMachine.get_from_heap(each_remaining).toString().pyData())

    @staticmethod
    def dump_instruction():
        for _code in BVirtualMachine.INSTRUCTIONS:
            print(_code.__str__())
        exit(1)


def load_builtins(_bytecode:ByteCodeChunk):
    ########## TEMPORARY LOADER ##############
    __x_builtins_x__ = tuple([{
        "symbol": "println",
        "param_count": 1,
        "return_type": BBuiltinObject.Null,
        "data_type": BBuiltinObject.BuiltinFunc,
        "points_to": BVirtualMachine.push_to_heap(BuiltinFunc("println", println)),
    }])

    for builtin in __x_builtins_x__:
        SymbolTable.insert(**builtin)

def push_const(_bytecode:ByteCodeChunk):
    BVirtualMachine.EVAL__STACK.append(_bytecode.getValueOf("mem_address"))
    # mark as zero ref
    BVirtualMachine.REFERENCE_COUNTER[len(BVirtualMachine.EVAL__STACK) - 1] = 0

def push_name(_bytecode:ByteCodeChunk):
    
    symbol_prop = SymbolTable.lookup(_bytecode.getValueOf("symbol"))
    
    if  not symbol_prop:
        # throws error
        return errorHandler.throw__error(
            errorType.NAME_ERROR, "\"" + _bytecode.getValueOf("symbol")+ "\" is not defined!",
            trace__token(_bytecode.getValueOf("raw"))
        )
    
    obj_pointed_address = symbol_prop["points_to"]

    # push to stack
    BVirtualMachine.EVAL__STACK.append(obj_pointed_address)

def push_attrib(_bytecode:ByteCodeChunk):
    top = BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK[-1])

    if  not top.__has_bound__(_bytecode.getValueOf("symbol")):
        # throws error
        errorHandler.throw__error(
            errorType.ATTRIBUTE_ERROR, top.typeString().pyData() + " does not contains attribute \"" + _bytecode.getValueOf("symbol") + "\"",
            trace__token(_bytecode.getValueOf("raw"))
        )
    # BVirtualMachine.EVAL__STACK.pop()
    attr_obj = top.__get_bound__(_bytecode.getValueOf("symbol"))
    attr_addr = BVirtualMachine.push_to_heap(attr_obj)
    BVirtualMachine.EVAL__STACK.append(attr_addr)

def store_func(_bytecode:ByteCodeChunk):
    symbol = _bytecode.getValueOf("symbol")
    obj_address = BVirtualMachine.EVAL__STACK.pop()

    var = SymbolTable.lookup(symbol)
    dtype = BVirtualMachine.get_from_heap(obj_address).typeString().pyData()

    if  var["data_type"] != dtype:
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "\"" + symbol + "\" is declaired as \"" + var["data_type"] + "\", got \"" + dtype + "\".",
            trace__token(var["token"])
        )

    SymbolTable.update(symbol, points_to =  obj_address)

    # increase ref count
    BVirtualMachine.increment_count(obj_address)

def store_name(_bytecode:ByteCodeChunk):
    symbol = _bytecode.getValueOf("symbol")
    obj_address = BVirtualMachine.EVAL__STACK.pop()
    var = SymbolTable.lookup(symbol)
    dtype = BVirtualMachine.get_from_heap(obj_address).typeString().pyData()
    
    if  var["data_type"] != dtype:
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "\"" + symbol + "\" is declaired as \"" + var["data_type"] + "\", got \"" + dtype + "\".",
            trace__token(var["token"])
        )

    SymbolTable.update(symbol, points_to = obj_address)

    # increase ref count
    BVirtualMachine.increment_count(obj_address)

def store_local(_bytecode:ByteCodeChunk):
    symbol = _bytecode.getValueOf("symbol")

    obj_address = BVirtualMachine.EVAL__STACK.pop()

    var = SymbolTable.lookup(symbol)
    dtype = BVirtualMachine.get_from_heap(obj_address).typeString().pyData()

    if  var["data_type"] != dtype:
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "\"" + symbol + "\" is declaired as \"" + var["data_type"] + "\", got \"" + dtype + "\".",
            trace__token(var["token"])
        )

    SymbolTable.update(symbol, points_to = obj_address)

    # increase ref count
    BVirtualMachine.increment_count(obj_address)


def binary_expr(_bytecode:ByteCodeChunk):
   
    lhs = BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK.pop())
    rhs = BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK.pop())

    opt = _bytecode.getValueOf("operator")
    opt_as_str = opt.getSymbol()

    if  not typeCheck(opt_as_str, lhs, rhs):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "invalid operator \"" + opt_as_str + "\" for operands " + lhs.typeString().pyData() + " and " + rhs.typeString().pyData() + "!",
            trace__token(opt)
        )

    new_obj = evaluate(opt_as_str, lhs.pyData(), rhs.pyData())
    object_address = BVirtualMachine.push_to_heap(new_obj)
    BVirtualMachine.EVAL__STACK.append(object_address)

def pop_top(_bytecode:ByteCodeChunk):
    BVirtualMachine.EVAL__STACK.pop()

def call_expr(_bytecode:ByteCodeChunk):

    call_operator = _bytecode.getValueOf("operator")
    call_args_count = _bytecode.getValueOf("arg_count")

    _must_be_callable = BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK.pop())
    if  _must_be_callable.typeString().pyData() not in (BBuiltinObject.Func, BBuiltinObject.BuiltinFunc, BBuiltinObject.BoundMethod):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, _must_be_callable.typeString().pyData() + "(" + _must_be_callable.toString().pyData() + ") is not callable!",
            trace__token(call_operator)
        )
    
    # otherwise callable
    func_name = _must_be_callable.getName()
    

    ############# BUILTIN CALL ####################
    if  _must_be_callable.typeString().pyData() == BBuiltinObject.BuiltinFunc:
        null = _must_be_callable.pyData()(BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK.pop()))
        mem_address = BVirtualMachine.push_to_heap(null)
        BVirtualMachine.EVAL__STACK.append(mem_address)
        return

    ############# BOUND CALL ####################
    if  _must_be_callable.typeString().pyData() == BBuiltinObject.BoundMethod:
        bound = _must_be_callable
        if  bound.paramc != call_args_count:
            # throws error
            return errorHandler.throw__error(
                errorType.TYPE_ERROR, "function " + func_name.pyData() + "(...) expected parameter count \"" + str(bound.paramc) + "\", got \"" + str(call_args_count) + "\".",
                trace__token(call_operator)
            )
        param = BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK.pop())
        result = bound.pyData()(param)
        mem_address = BVirtualMachine.push_to_heap(result)
        BVirtualMachine.EVAL__STACK.append(mem_address)
        return
    

    ########### FUNCTION #########################
    symbol_prop = SymbolTable.lookup(func_name.pyData())

    if  symbol_prop["param_count"] != call_args_count:
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "function " + func_name.pyData() + "(...) expected parameter count \"" + str(symbol_prop["param_count"]) + "\", got \"" + str(call_args_count) + "\".",
            trace__token(call_operator)
        )
    
    BVirtualMachine.SCOPE_STACK.append(SymbolTable.CURR)
    SymbolTable.CURR = symbol_prop["function_scope"]

    # push func name for monitoring
    if  len(BVirtualMachine.NAMED_CALL_STACK) <= 0:
        BVirtualMachine.CALL_COUNTER[func_name.pyData()] = 1
        BVirtualMachine.NAMED_CALL_STACK.append(func_name.pyData())
    else:
       
        if  BVirtualMachine.NAMED_CALL_STACK[-1] == func_name.pyData():
            BVirtualMachine.CALL_COUNTER[func_name.pyData()] += 1
        else:
            BVirtualMachine.NAMED_CALL_STACK.append(func_name.pyData())

    # push function instructions
    func_code = _must_be_callable.getByteCode()
    BVirtualMachine.push_frame(func_code.getInstructions())

    # record last pointer
    # add 1 to skip function call
    BVirtualMachine.CONTROLL_HISTORY.append(BVirtualMachine.POINTER + 1)
    BVirtualMachine.POINTER = 0

def return_opcode(_bytecode:ByteCodeChunk):
    BVirtualMachine.STACK_FRAME.pop()
    BVirtualMachine.POINTER = BVirtualMachine.CONTROLL_HISTORY.pop()

    # return if source file!
    if  len(BVirtualMachine.NAMED_CALL_STACK) <= 0:
        return
    
    if  len(BVirtualMachine.SCOPE_STACK) > 0:
        SymbolTable.CURR = BVirtualMachine.SCOPE_STACK.pop()

    # function name call ended
    func_name = BVirtualMachine.NAMED_CALL_STACK.pop()
    func_prop = SymbolTable.lookup(func_name)

    BVirtualMachine.CALL_COUNTER.pop(func_name)

    actual_return = BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK[-1]) # top

    if  func_prop["return_type"] != actual_return.typeString().pyData():
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, func_name + "(...) expected return type is \"" + func_prop["return_type"] + "\", but returned \"" + actual_return.typeString().pyData() + "\".",
            trace__token(func_prop["token"])
        )