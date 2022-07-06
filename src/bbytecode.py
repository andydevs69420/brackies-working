from enum import Enum
from berrhandler import errorType, errorHandler


class OpCode(Enum):
    LOAD_BUILTINS   = "load_builtins"
    NO_OP           = "no_op"
    PUSH_CONST      = "push_const"
    PUSH_NAME       = "push_name"
    PUSH_ATTRIB     = "push_attrib"
    STORE_FUNC      = "store_func"
    STORE_NAME      = "store_name"
    STORE_LOCAL     = "store_local"
    BINARY_EXPR     = "binary_expr"
    POP_TOP         = "pop_top"
    CALL            = "call"
    RETURN          = "return"


class ByteCodeChunk:
    def __init__(self, **_atrtib):
        self.__required = tuple([
            ("line"  , int   ),
            ("opcode", OpCode),
            # ("last_line"  , int   ),
        ])

        for req in self.__required:
            if  req[0] not in _atrtib.keys():
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "required key \"" + req[0] + "\" is not defined!",
                )
            if  type(_atrtib[req[0]]) != req[1]:
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "required key \"" + req[0] + "\" type \"" + type(_atrtib[req[0]]).name + "\" != \"" + req[1].name + "\".",
                )

        self.__attrib = _atrtib  
    
    def getLine(self):
        return self.__attrib["line"]

    def getOpcode(self):
        return self.__attrib["opcode"]

    def getLastLine(self):
        return self.__attrib["line"] + 1
    
    def getKeys(self):
        return self.__attrib.keys()
    
    def getValueOf(self, _key:str):
        if  _key not in self.__attrib.keys():
            # throws error
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "key \"" + _key + "\" does not exist in " + self.__attrib.keys().__str__() + "!",
            )
        return self.__attrib[_key]

    def __str__(self):
        _not_required = ""
        _separator = " -- "
        for k, v in zip(self.__attrib.keys(), self.__attrib.values()):
            if  k not in [req_key[0] for req_key in self.__required ]:
                _not_required += v.__str__()
                _not_required += _separator
        
        if  _not_required.endswith(_separator):
            _not_required = _not_required[: len(_not_required) - len(_separator)]

        return type(self).__name__ + "(" + "[" + str(self.__attrib["line"]) + "]" + _separator + self.__attrib["opcode"].name + _separator + _not_required + ")"

