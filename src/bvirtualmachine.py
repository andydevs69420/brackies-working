from blogger import log__info
from core.bobject import *
from btoken import trace__token
from bsymboltable import SymbolTable
from core.bcore import println, scan, typeCheck, evaluate, write, readFile
from bbytecode import OpCode, ByteCodeChunk
from berrhandler import errorHandler, errorType
class BVirtualMachine:pass


class StackFrame:
    MAX_FRAME_SIZE = 40000

    def __init__(self):
        self.__internal      = []
        self.__local_data    = []
        self.__has_new_frame = False
    
    def push_local(self,_obj:Obj):
        self.__local_data[-1].append(_obj)
        return len(self.__local_data[-1]) - 1
    
    def get_local(self, _index:int):
        return self.__local_data[-1][_index]
    
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
        self.__local_data.append([])
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
        self.__local_data.pop()
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
            BVirtualMachine.POINTER += 1
            return
        elif  _opcode == OpCode.PUSH_CONST:
            return push_const(_bytecode)
        elif  _opcode == OpCode.BUILD_LIST:
            return build_list(_bytecode)
        elif _opcode == OpCode.PUSH_NAME:
            return push_name(_bytecode)
        elif _opcode == OpCode.PUSH_LOCAL:
            return push_local(_bytecode)
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
        elif _opcode == OpCode.IF_ZERO_NULL_OR_FALSE:
            return if_zero_null_or_false(_bytecode)
        elif _opcode == OpCode.JUMP_TO:
            return jump_to(_bytecode)
        else:
            for _code in BVirtualMachine.INSTRUCTIONS:
                print(_code.__str__())
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "not implemented opcode \"" + _opcode.name + "\"!"
            )

    @staticmethod
    def run():
        # for _code in BVirtualMachine.INSTRUCTIONS:
        #     print(_code.__str__())
        # return

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
                # print(f"## EXECUTE: {current_frame[BVirtualMachine.POINTER]}")
                BVirtualMachine.execute_byte(current_frame[BVirtualMachine.POINTER])
                if BVirtualMachine.STACK_FRAME.isempty() or BVirtualMachine.STACK_FRAME.hasNewFrame():
                    break
                
                # print("STUCK!!", current_frame[BVirtualMachine.POINTER])
            
            
        log__info("Finished!")
        # for each_remaining in BVirtualMachine.EVAL__STACK:
        #     log__info(get__from_heap(each_remaining).toString().pyData())

    @staticmethod
    def dump_instruction():
        for _code in BVirtualMachine.INSTRUCTIONS:
            print(_code.__str__())
        errorHandler.throw__error(
            errorType.UNEXPECTED_ERROR, "vm dumped!!"
        )




####################### USABLE FUNCTIONS ###########################



########### HEAPM OPERATIONS ###########
# gets object stored in virtual heap memory
def get__from_heap(_address:int):
    return BVirtualMachine.get_from_heap(_address)

# stores an object to heap
def push__to_heap(_obj:Obj):
    return BVirtualMachine.push_to_heap(_obj)

########### STACK OPERATIONS ###########
# pushes target address to eval stack
def push__to_estack(_address:int):
    return BVirtualMachine.EVAL__STACK.append(_address)

# pop target address from eval stack
def pop__from_estack():
    return BVirtualMachine.EVAL__STACK.pop()

# gets top index
def estack_get_top():
    return len(BVirtualMachine.EVAL__STACK) - 1



def forward_ip(_address):
    BVirtualMachine.POINTER = _address


############################ START ################################

def load_builtins(_bytecode:ByteCodeChunk):
    ########## TEMPORARY LOADER ##############
    __x_builtins_x__ = tuple([({
        "symbol": "write",
        "param_count": 1,
        "return_type": BBuiltinObject.Null,
        "data_type": BBuiltinObject.BuiltinFunc,
        "points_to": push__to_heap(BuiltinFunc("write", write)),
    }), ({
        "symbol": "println",
        "param_count": 1,
        "return_type": BBuiltinObject.Null,
        "data_type": BBuiltinObject.BuiltinFunc,
        "points_to": push__to_heap(BuiltinFunc("println", println)),
    }), ({
        "symbol": "scan",
        "param_count": 1,
        "return_type": BBuiltinObject.Str,
        "data_type": BBuiltinObject.BuiltinFunc,
        "points_to": push__to_heap(BuiltinFunc("scan", scan)),
    }), ({
        "symbol": "readFile",
        "param_count": 1,
        "return_type": BBuiltinObject.Str,
        "data_type": BBuiltinObject.BuiltinFunc,
        "points_to": push__to_heap(BuiltinFunc("readFile", readFile)),
    })])

    for each_builtin in __x_builtins_x__:
        SymbolTable.insert(**each_builtin)
    
    forward_ip(BVirtualMachine.POINTER + 1)

def push_const(_bytecode:ByteCodeChunk):
    push__to_estack(_bytecode.getValueOf("bobject"))
    forward_ip(BVirtualMachine.POINTER + 1)

def build_list(_bytecode:ByteCodeChunk):
    element_size = _bytecode.getValueOf("length")

    new_list = List()

    for ____ in range(element_size):
        actual_obj = pop__from_estack()
        new_list.push(actual_obj)
    
    push__to_estack(new_list)

    forward_ip(BVirtualMachine.POINTER + 1)

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
    push__to_estack(get__from_heap(obj_pointed_address))

    forward_ip(BVirtualMachine.POINTER + 1)

def push_local(_bytecode:ByteCodeChunk):
    
    symbol_prop = SymbolTable.lookup(_bytecode.getValueOf("symbol"))
    
    if  not symbol_prop:
        # throws error
        return errorHandler.throw__error(
            errorType.NAME_ERROR, "\"" + _bytecode.getValueOf("symbol")+ "\" is not defined!",
            trace__token(_bytecode.getValueOf("raw"))
        )

    obj_pointed_address = symbol_prop["points_to"]

    push__to_estack(BVirtualMachine.STACK_FRAME.get_local(obj_pointed_address))

    forward_ip(BVirtualMachine.POINTER + 1)

def push_attrib(_bytecode:ByteCodeChunk):
    top = pop__from_estack()

    if  not top.__has_bound__(_bytecode.getValueOf("symbol")):
        # throws error
        errorHandler.throw__error(
            errorType.ATTRIBUTE_ERROR, top.typeString().pyData() + " does not contains attribute \"" + _bytecode.getValueOf("symbol") + "\"",
            trace__token(_bytecode.getValueOf("raw"))
        )
    # pop__from_estack()
    attr_obj = top.__get_bound__(_bytecode.getValueOf("symbol"))
    push__to_estack(attr_obj)

    forward_ip(BVirtualMachine.POINTER + 1)

def store_func(_bytecode:ByteCodeChunk):
    symbol = _bytecode.getValueOf("symbol")

    obj = pop__from_estack()

    function = SymbolTable.lookup(symbol)
    datatype = (obj.typeString().pyData())

    if  function["data_type"] != datatype and not (function["data_type"] == BBuiltinObject.Any and (datatype in BRACKIES_TYPE or datatype.startswith("List_of_"))):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "\"" + symbol + "\" is declaired as \"" + function["data_type"] + "\", got \"" + datatype + "\".",
            trace__token(function["token"])
        )

    obj_address = push__to_heap(obj)
    
    # update index where it is pointed
    SymbolTable.update(symbol, points_to = obj_address)

    # increase ref count
    BVirtualMachine.increment_count(obj_address)

    forward_ip(BVirtualMachine.POINTER + 1)

def store_name(_bytecode:ByteCodeChunk):
    symbol = _bytecode.getValueOf("symbol")
    
    obj = pop__from_estack()

    global_v = SymbolTable.lookup(symbol)
    datatype = (obj.typeString().pyData())

    if  global_v["data_type"] != datatype and not (global_v["data_type"] == BBuiltinObject.Any and (datatype in BRACKIES_TYPE or datatype.startswith("List_of_"))):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "\"" + symbol + "\" is declaired as \"" + global_v["data_type"] + "\", got \"" + datatype + "\".",
            trace__token(global_v["token"])
        )
    
    obj_address = push__to_heap(obj)
    
    # update index where it is pointed
    SymbolTable.update(symbol, points_to = obj_address)

    # increase ref count
    BVirtualMachine.increment_count(obj_address)

    forward_ip(BVirtualMachine.POINTER + 1)

def store_local(_bytecode:ByteCodeChunk):
    symbol = _bytecode.getValueOf("symbol")

    obj = pop__from_estack()

    localvar = SymbolTable.lookup(symbol)
    datatype = (obj.typeString().pyData())

    if  localvar["data_type"] != datatype and not (localvar["data_type"] == BBuiltinObject.Any and (datatype in BRACKIES_TYPE or datatype.startswith("List_of_"))):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "\"" + symbol + "\" is declaired as \"" + localvar["data_type"] + "\", got \"" + datatype + "\".",
            trace__token(localvar["token"])
        )

    obj_address = BVirtualMachine.STACK_FRAME.push_local(obj)

    # update index where it is pointed
    SymbolTable.update(symbol, points_to = obj_address)

    forward_ip(BVirtualMachine.POINTER + 1)


def binary_expr(_bytecode:ByteCodeChunk):
   
    lhs = pop__from_estack()
    rhs = pop__from_estack()

    opt = _bytecode.getValueOf("operator")
    opt_as_str = opt.getSymbol()

    if  not typeCheck(opt_as_str, lhs, rhs):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, "invalid operator \"" + opt_as_str + "\" for operands " + lhs.typeString().pyData() + " and " + rhs.typeString().pyData() + "!",
            trace__token(opt)
        )

    new_obj = evaluate(opt_as_str, lhs.pyData(), rhs.pyData())
    push__to_estack(new_obj)

    forward_ip(BVirtualMachine.POINTER + 1)

def pop_top(_bytecode:ByteCodeChunk):
    pop__from_estack()
    forward_ip(BVirtualMachine.POINTER + 1)

def call_expr(_bytecode:ByteCodeChunk):

    call_operator = _bytecode.getValueOf("operator")
    call_args_count = _bytecode.getValueOf("arg_count")

    _must_be_callable = pop__from_estack()
    
    if  _must_be_callable.typeString().pyData() not in (BBuiltinObject.Func, BBuiltinObject.BuiltinFunc, BBuiltinObject.BoundMethod):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, _must_be_callable.typeString().pyData() + "(" + _must_be_callable.toString().pyData() + ") is not callable!",
            trace__token(call_operator)
        )
    
    # otherwise callable
    func_name = _must_be_callable.getName()

    ############# BUILTIN CALL ##################
    if  _must_be_callable.typeString().pyData() == BBuiltinObject.BuiltinFunc:
        forward_ip(BVirtualMachine.POINTER + 1)
        symbol_prop = SymbolTable.lookup(func_name.pyData())
        builtin = _must_be_callable
        
        if  symbol_prop["param_count"] != call_args_count:
            # throws error
            return errorHandler.throw__error(
                errorType.TYPE_ERROR, "function " + func_name.pyData() + "(...) expected parameter count \"" + str(symbol_prop["param_count"]) + "\", got \"" + str(call_args_count) + "\".",
                trace__token(call_operator)
            )
        
        func_param_stack = FunctionParameter()
        for _____ in range(call_args_count):
            func_param_stack.push(pop__from_estack())
        
        result = builtin.pyData()(func_param_stack)
        return push__to_estack(result)

    ############# BOUND CALL ####################
    if  _must_be_callable.typeString().pyData() == BBuiltinObject.BoundMethod:
        forward_ip(BVirtualMachine.POINTER + 1)
        bound = _must_be_callable
        if  bound.paramc != call_args_count:
            # throws error
            return errorHandler.throw__error(
                errorType.TYPE_ERROR, "function " + func_name.pyData() + "(...) expected parameter count \"" + str(bound.paramc) + "\", got \"" + str(call_args_count) + "\".",
                trace__token(call_operator)
            )
        
        func_param_stack = FunctionParameter()
        for _____ in range(call_args_count):
            func_param_stack.push(pop__from_estack())

        result = bound.pyData()(func_param_stack)
        return push__to_estack(result)
    

    ################### FUNCTION #################
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
            BVirtualMachine.CALL_COUNTER[func_name.pyData()] = 1
            BVirtualMachine.NAMED_CALL_STACK.append(func_name.pyData())

    # push function instructions
    func_code = _must_be_callable.getByteCode()
    BVirtualMachine.push_frame(func_code.getInstructions())

    # record last pointer
    # add 1 to skip function call
    BVirtualMachine.CONTROLL_HISTORY.append(BVirtualMachine.POINTER + 1)
    forward_ip(0)

def return_opcode(_bytecode:ByteCodeChunk):
    # print("EVAL: ", BVirtualMachine.EVAL__STACK)
    # print(BVirtualMachine.get_from_heap(BVirtualMachine.EVAL__STACK[-1]))
    BVirtualMachine.STACK_FRAME.pop()
    forward_ip(BVirtualMachine.CONTROLL_HISTORY.pop())
    # print(f"RESTORED AT: {BVirtualMachine.POINTER * 2}")

    # return if source file!
    if  len(BVirtualMachine.NAMED_CALL_STACK) <= 0:
        return
    
    if  len(BVirtualMachine.SCOPE_STACK) > 0:
        SymbolTable.CURR = BVirtualMachine.SCOPE_STACK.pop()

    # function name call ended
    func_name = BVirtualMachine.NAMED_CALL_STACK.pop()
    func_prop = SymbolTable.lookup(func_name)

    BVirtualMachine.CALL_COUNTER.pop(func_name)

    actual_return = BVirtualMachine.EVAL__STACK[-1] # top

    if  func_prop["return_type"] != actual_return.typeString().pyData() and not (func_prop["return_type"] == BBuiltinObject.Any and (actual_return.typeString().pyData() in BRACKIES_TYPE or actual_return.typeString().pyData().startswith("List_of_"))):
        # throws error
        return errorHandler.throw__error(
            errorType.TYPE_ERROR, func_name + "(...) expected return type is \"" + func_prop["return_type"] + "\", but returned \"" + actual_return.typeString().pyData() + "\".",
            trace__token(func_prop["token"])
        )
    

def if_zero_null_or_false(_bytecode:ByteCodeChunk):
    
    top = pop__from_estack()
    jump_loc = _bytecode.getValueOf("jump_loc")

    if  not top.pyData():
        forward_ip((jump_loc//2))
    else:
        forward_ip(BVirtualMachine.POINTER + 1)
    # print(_bytecode)
    # print(f"JUMPING TO", BVirtualMachine.INSTRUCTIONS[BVirtualMachine.POINTER])
    # exit(1)
    
def jump_to(_bytecode:ByteCodeChunk):
    jump_loc = _bytecode.getValueOf("jump_loc")
    forward_ip((jump_loc//2))
    

