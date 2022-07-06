
from bbytecode import ByteCodeChunk
from berrhandler import errorHandler, errorType


class BBuiltinObject:
    Obj  = "Obj"
    Type = "Type"
    Num  = "Num"
    Int  = "Int"
    Flt  = "Flt"
    Str  = "Str"
    Bool = "Bool"
    Null = "Null"
    List = "List"
    Dict = "Dict"
    BuiltinFunc  = "BuiltinFunc"
    BoundMethod  = "BoundMethod"
    BrackiesCode = "BrackiesCode"
    Func = "Func"

__ALL__ = [ 
    BBuiltinObject.Obj,
    BBuiltinObject.Type,
    BBuiltinObject.Num,
    BBuiltinObject.Int,
    BBuiltinObject.Flt,
    BBuiltinObject.Str,
    BBuiltinObject.Bool,
    BBuiltinObject.Null,
    BBuiltinObject.List,
    BBuiltinObject.Dict,
    BBuiltinObject.BuiltinFunc,
    BBuiltinObject.BoundMethod,
    BBuiltinObject.BrackiesCode,
    BBuiltinObject.Func,
]


BRACKIES_TYPE = __ALL__

class Obj:pass
class Type:pass
class Num:pass
class Int:pass
class Flt:pass
class Str:pass
class Bool:pass
class Null:pass
class LIST:pass #TODO: implement
class DICT:pass #TODO: implement
class FUNC:pass
class BuiltinFunc:pass
class BoundMethod:pass


class FunctionParameter(object):
    def __init__(self):
        self.__params:list[Obj] = []
    
    def push(self, _obj:Obj):
        self.__params.append(_obj)
    
    def pop(self):
        return self.__params.pop()

    def top(self):
        return self.__params[-1]


class Obj_Interface(object):

    def __init__(self):
        self.boundmethods = ({})
    
    #bound: [toString => Str]
    def type(self, _param:FunctionParameter=None):
        return Type(self)

    #bound: [toString => Str]
    def typeString(self, _param:FunctionParameter=None):
        return Str(f"{ type(self).__name__ }")

    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return Str(f"{ type(self).__name__ }(id = { hex(id(self)) })")
    

    def __has_bound__(self, _bound:str):
        if  _bound in self.boundmethods.keys():
            return True
        return False
    
    def __add_bound__(self, _name:str, _argc:int, _callable:callable,):
        self.boundmethods[_name] = BoundMethod(_name, _argc, _callable)
    
    def __get_bound__(self, _name:str):
        if  not self.__has_bound__(_name):
            # throws error
            errorHandler.throw__error(
                errorType.ATTRIBUTE_ERROR, type(self).__name__ + " does not contains method \"" + _name + "\"."
            )
        return self.boundmethods[_name]


class Obj(Obj_Interface):
    def __init__(self):
        super().__init__()
        self.__add_bound__("type"      , 0, self.type      )
        self.__add_bound__("typeString", 0, self.typeString)
        self.__add_bound__("toString"  , 0, self.toString  )



class Type(Obj):
    def __init__(self, _obj:Obj):
        super().__init__()
        self.dtype = _obj
        self.__add_bound__("equals", 1, self.equals)
    
    def pyData(self):
        return type(self.dtype)
    
    #bound: [equals => Bool]
    def equals(self, _param:FunctionParameter=None):
        return Bool(self.pyData() == _param.pop().type().pyData())

    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return Str(f"{type(self).__name__}(type = {type(self.dtype).__name__})")


################## BUILTIN DATATYPE ####################
class Num(Obj):
    def __init__(self, _any_number:int or float):
        super().__init__()
        self.host_data = _any_number
    
    def pyData(self):
        return self.host_data

    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return Str(f"{self.host_data}")
    
    def __str__(self):
        return self.toString().pyData()

class Int(Num):
    def __init__(self, _any_number: int or float):
        super().__init__(_any_number)

class Flt(Num):
    def __init__(self, _any_number: int or float):
        super().__init__(_any_number)

class Str(Obj):
    def __init__(self, _str:str):
        super().__init__()
        self.host_data = _str
        self.__add_bound__("equals", 1, self.equals)
        self.__add_bound__("concat", 1, self.concat)
    
    def pyData(self):
        return self.host_data
    

    #bound: [equals => Bool]
    def equals(self, _str_other:FunctionParameter):
        if  type(_str_other.top()) != Str:return Bool(False)
        return Bool(self.host_data == _str_other.pop().pyData())

    #bound: [concat => Str]
    def concat(self, _str_other:FunctionParameter):
        if  type(_str_other.top()) != Str:return Bool(False)
        return Str(self.host_data + _str_other.pop().pyData())

    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return self
    
    def __str__(self):
        return self.pyData()

class Bool(Obj):
    def __init__(self, _bool:bool):
        super().__init__()
        self.host_data = _bool
    
    def pyData(self):
        return self.host_data

    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return Str("true" if self.host_data else "false")
    
    def __str__(self):
        return self.toString().pyData()

class Null(Obj):
    def __init__(self, _none:None):
        super().__init__()
        self.host_data = _none
    
    def pyData(self):
        return self.host_data

    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return Str("null")
    
    def __str__(self):
        return self.toString().pyData()




########################## FUNCTION #############################

class BuiltinFunc(Obj):
    def __init__(self, _name:str, _function:callable):
        super().__init__()
        self.name     = _name
        self.function = _function
        self.__add_bound__("getName", 0, self.getName)
    
    def pyData(self):
        return self.function
    
    #bound: [getName => Str]
    def getName(self, _param:FunctionParameter=None):
        return Str(self.name)
    
    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return Str(f"{ type(self).__name__ }(id = { hex(id(self)) }, name = {self.name})")
    
    def __str__(self):
        return self.toString().pyData()

class BoundMethod(Obj):
    def __init__(self, _name:str, _param_count:int, _callable:callable):
        # Do not initialize super!!!
        self.boundmethods = ({})
        ###########################
        self.name = _name
        self.paramc = _param_count
        self.callable = _callable
    
    def pyData(self):
        return self.callable
    
    #bound: [getName => Str]
    def getName(self, _param:FunctionParameter=None):
        return Str(self.name)
    
    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return  Str(f"{ type(self).__name__ }(id = { hex(id(self)) }, name = {self.name})")
    
    def __str__(self):
        return self.toString().pyData()


##################       OTHERS      ##################
class BrackiesCode(Obj):
    def __init__(self, _code:list[ByteCodeChunk]):
        super().__init__()
        self.instructions = _code

    def getInstructions(self):
        return self.instructions
    
    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        string = ""
        index = 0
        for i in self.instructions:
            string += i.__str__()
            if index < len(self.instructions) - 1:
                string += ", "
            index += 1

        return Str("[" + string + "]")

class Func(Obj):
    def __init__(self, _name:str, _bytecode:BrackiesCode):
        super().__init__()
        self.name = _name
        self.bytecode = _bytecode
        self.__add_bound__("getName"    , 0, self.getName    )
        self.__add_bound__("getByteCode", 0, self.getByteCode)
    
    #bound: [getName => Str]
    def getName(self, _param:FunctionParameter=None):
        return Str(self.name)
    
    #bound: [getByteCode => BrackiesCode]
    def getByteCode(self, _param:FunctionParameter=None):
        return self.bytecode
    
    #bound: [toString => Str]
    def toString(self, _param:FunctionParameter=None):
        return Str(f"{ type(self).__name__ }(id = { hex(id(self)) }, name = {self.name})")
    
    def __str__(self):
        return self.toString().pyData()
