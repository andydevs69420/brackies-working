from ctypes import addressof
from enum import Enum
import opcode
from bvirtualmachine import VirtualMachine
from core.bobject import *
from bsymboltable import SymbolTable, SymbolType
from blogger import log__info, log__error
from bbytecode import OpCode, ByteCodeChunk
from berrhandler import errorType, errorHandler
from btoken import BTokenType, BToken, trace__token


class AccessModifier(Enum):
    PUBLIC    = 0x00
    PRIVATE   = 0x01
    PROTECTED = 0x02

class MemberType(Enum):
    TYPE_MEMBER     = 0x00
    INSTANCE_MEMBER = 0x01


class BNode(object):

    LINE = 0
    CODE = []
    FUNC = []
    

    @staticmethod
    def getLine():
        BNode.LINE += 2
        return (BNode.LINE - 2)
    
    @staticmethod
    def putCode(_bytecode:ByteCodeChunk):
        BNode.CODE.append(_bytecode)
    
    ####################################################

    def __init__(self, **_attrib):
        self.__attr = _attrib
    
    def validate(self, _required:tuple[tuple]):
        for req in _required:
            if  req[0] not in self.__attr.keys():
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! required key \"" + req[0] + "\" is not available!"
                )
            if  (not isinstance(self.__attr[req[0]], req[1])) and (self.__attr[req[0]] == None and req[1] == None):
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! required type for key \"" + req[0] + "\" does not match. " + req[1].__name__ + " != " + type(self.__attr[req[0]]).__name__
                )
        # success | valid flag
        return True

    def getPath(self):return self.__path
    def getCont(self):return self.__cont
    def getAttr(self):return self.__attr
    def compile(self):
        pass
    def compile(self):
        pass


########################## INDIVIDUAL NODE ##########################

class SourceCodeNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("statements", tuple),
        ))
    
    def compile(self):
        # info
        log__info("analyzing source code...")

        # attrib
        attributes = self.getAttr()

        # new scope
        SymbolTable.new_scope()

        for stmnt in attributes["statements"]:
            stmnt.compile()
        
        # end new scope
        SymbolTable.end_scope()

        for i in BNode.CODE:
            print(i)

        # return code
        return self.CODE

class GlobalVariableNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("decl", tuple),
        ))
    
    def compile(self):
        # info
        log__info("analyzing global variable...")

        # attrib
        attributes = self.getAttr()

class ConstVariableNode(GlobalVariableNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)

class LocalVariableNode(GlobalVariableNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
    
    def compile(self):
        # info
        log__info("analyzing local variable...")

        # attrib
        attributes = self.getAttr()


############# USER DEFINED OBJECT #####
class ClassNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("class_name", BToken),
            ("class_body", tuple ),
        ))
    
    def compile(self):
        # info
        log__info("analyzing user defined types...")

        # attrib
        attributes = self.getAttr()
        
        ########
        class_name:BToken = attributes["class_name"]
        class_name_as_str = class_name.getSymbol()

        if  SymbolTable.lookup(class_name_as_str):
            # throws error
            return errorHandler.throw__error(
                errorType.NAME_ERROR, "class \"" + class_name_as_str + "\" is already defined!",
                trace__token(class_name)
            )

        # new scope
        SymbolTable.new_scope()

        for each_prop in attributes["class_body"]:
            member = each_prop.compile()
            if  member["node"] == ClassFunctionNode:
                print(member)
            else:
                print(member)

        # end new scope
        SymbolTable.end_scope()

        #######################

        # return code
        return self.CODE
    
############# USER DEFINED OBJECT #####
class ExtendedClassNode(ClassNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("class_name" , BToken),
            ("super_class", BToken),
            ("class_body" , tuple ),
        ))
    
    def compile(self):
        # info
        log__info("analyzing extended user defined types...")

class AccessModNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            ("access_modifier", AccessModifier),
            ("prop", BNode)
        ))
    
    def compile(self):
        # info
        log__info("analyzing access modifier...")

        # attrib
        attributes = self.getAttr()

        # access
        _access = attributes["access_modifier"]
        
        _prop = (attributes["prop"]
                    .compile())
        
        return {"member_type":MemberType.INSTANCE_MEMBER, **_prop, "node": type(attributes["prop"]), "access":_access}

class StaticNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            ("static_prop", BNode),
        ))
    
    def compile(self):
        # info
        log__info("analyzing static...")

        # attributes
        attributes = self.getAttr()

        # prop
        _prop = (attributes["static_prop"]
                    .compile())
        
        return {**_prop, "member_type":MemberType.TYPE_MEMBER}
        

class ClassVarNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            ("decl", tuple),
        ))

class ClassFunctionNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("func_name"  , BToken  ),
            ("return_type", TypeNode),
            ("parameters" , tuple   ),
            ("func_body"  , tuple   ),
        ))
    
    def compile(self):
        # info
        log__info("analyzing class function...")
        
        # attrib
        attributes = self.getAttr()

        # func name
        _func_name:BToken = attributes["func_name"]
        _func_name_as_str = _func_name.getSymbol()

        # return type
        _func_return = (attributes["return_type"]
                        .compile())

        # append current func
        BNode.FUNC.append((_func_name, _func_return))

        ####### MAKE COPY #######
        _line = BNode.LINE
        _code = BNode.CODE
        ####### RESET ALL #######
        BNode.LINE = 0
        BNode.CODE = []

        # new scope
        SymbolTable.new_scope()

        ### PARAMETERS
        for each_param in attributes["parameters"]:
            # parameter name
            _param_name:BToken = each_param[0]
            _param_name_as_str = _param_name.getSymbol()

            # parameter datatype
            _param_type = (each_param[1]
                            .compile())

            ## CHECK EXISTENCE
            if  SymbolTable.existL(_param_name_as_str):
                # throws error
                return errorHandler.throw__error(
                    errorType.NAME_ERROR, "parameter \"" + _param_name_as_str + "\" is already defined!",
                    trace__token(_param_name)
                )

            # save param to symbol table
            _address = SymbolTable.insert(
                symbol   = _param_name_as_str,
                datatype = _param_type,
            )

            # push instructions
            self.putCode(ByteCodeChunk(
                line = self.getLine(), opcode = OpCode.STORE_LOCAL, symbol = _param_name_as_str, address = _address 
            ))

        ### FUNCTION BODY
        for each_node in attributes["func_body"]:
            each_node.compile()
        
        if  len(BNode.FUNC) > 0:
        
            ### DEFAULT RETURN
            if  BNode.FUNC[-1][1] != BBuiltinObject.Null:
                # throws error
                return errorHandler.throw__error(
                    errorType.TYPE_ERROR, "function \"" + BNode.FUNC[-1][0].getSymbol() + "\" is declaired as \"" + BNode.FUNC[-1][1] + "\" got \"" + BBuiltinObject.Null + "\"",
                    trace__token(BNode.FUNC[-1][0])
                )
            else:
                # push const opcode
                self.putCode(ByteCodeChunk(
                    line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = BBuiltinObject.Null, obj = Null(None)
                ))

                # return opcode
                self.putCode(ByteCodeChunk(
                    line = self.getLine(), opcode = OpCode.RETURN
                ))
            
                # pop current function
                BNode.FUNC.pop()

        # end new scope
        SymbolTable.end_scope()

        # function object
        _func = Func(_func_name_as_str, BrackiesCode(BNode.CODE))

        #######  RESTORE  #######
        BNode.LINE = _line
        BNode.CODE = _code

        ############ RETURN FUNCTION ############
        return {
            "function": _func_name_as_str,
            "function_token": _func_name,
            "function_obj": _func
        }

class FunctionNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("func_name"  , BToken  ),
            ("return_type", TypeNode),
            ("parameters" , tuple   ),
            ("func_body"  , tuple   ),
        ))
    
    def compile(self):
        # info
        log__info("analyzing function...")
        
        # attributes
        attributes = self.getAttr()

        # func name
        _func_name:BToken = attributes["func_name"]
        _func_name_as_str = _func_name.getSymbol()

        # return type
        _func_return = (attributes["return_type"]
                        .compile())

        # append current func
        BNode.FUNC.append((_func_name, _func_return))

        ####### MAKE COPY #######
        _line = BNode.LINE
        _code = BNode.CODE
        ####### RESET ALL #######
        BNode.LINE = 0
        BNode.CODE = []

        # new scope
        SymbolTable.new_scope()

        ### PARAMETERS
        for each_param in attributes["parameters"]:
            # parameter name
            _param_name:BToken = each_param[0]
            _param_name_as_str = _param_name.getSymbol()

            # parameter datatype
            _param_type = (each_param[1]
                            .compile())

            ## CHECK EXISTENCE
            if  SymbolTable.existL(_param_name_as_str):
                # throws error
                return errorHandler.throw__error(
                    errorType.NAME_ERROR, "parameter \"" + _param_name_as_str + "\" is already defined!",
                    trace__token(_param_name)
                )

            # save param to symbol table
            _address = SymbolTable.insert(
                symbol   = _param_name_as_str,
                datatype = _param_type,
            )

            # push instructions
            self.putCode(ByteCodeChunk(
                line = self.getLine(), opcode = OpCode.STORE_LOCAL, symbol = _param_name_as_str, address = _address 
            ))

        ### FUNCTION BODY
        for each_node in attributes["func_body"]:
            each_node.compile()
        
        if  len(BNode.FUNC) > 0:
        
            ### DEFAULT RETURN
            if  BNode.FUNC[-1][1] != BBuiltinObject.Null:
                # throws error
                return errorHandler.throw__error(
                    errorType.TYPE_ERROR, "function \"" + BNode.FUNC[-1][0].getSymbol() + "\" is declaired as \"" + BNode.FUNC[-1][1] + "\" got \"" + BBuiltinObject.Null + "\"",
                    trace__token(BNode.FUNC[-1][0])
                )
            else:
                # push const opcode
                self.putCode(ByteCodeChunk(
                    line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = BBuiltinObject.Null, obj = Null(None)
                ))

                # return opcode
                self.putCode(ByteCodeChunk(
                    line = self.getLine(), opcode = OpCode.RETURN
                ))
            
                # pop current function
                BNode.FUNC.pop()

        # end new scope
        SymbolTable.end_scope()

        # function object
        _func = Func(_func_name_as_str, BrackiesCode(BNode.CODE))

        #######  RESTORE  #######
        BNode.LINE = _line
        BNode.CODE = _code

        ############ SAVE FUNCTION ############
        _address = SymbolTable.insert(
            symbol   = _func_name_as_str,
            token    = _func_name,
            datatype = _func_return,
            mem_address = VirtualMachine.allocate()
        )

        # push const opcode
        self.putCode(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = _func_name_as_str, obj = _func
        ))

        # store func opcode
        self.putCode(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.STORE_FUNC, symbol = _func_name_as_str, address = _address
        ))

class IfNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("condition", BNode),
            ("statement", BNode),
        ))
    
    def compile(self):
        # info
        log__info("analyzing if statement...")

        # attrib
        attributes = self.getAttr()

        
class IfElseNode(IfNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("condition"     , BNode),
            ("statement"     , BNode),
            ("else_statement", BNode),
        ))
    
    def compile(self):
        # info
        log__info("analyzing if else...")

        # attrib
        attributes = self.getAttr()

class SwitchNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            ("switch_cond", BNode),
            ("switch_body", tuple),
        ))

class DoWhileNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("condition"    , BNode),
            ("do_while_body", BNode),
        ))
    
    def compile(self):
        # info
        log__info("analyzing do while loop...")

        # attrib
        attributes = self.getAttr()

class WhileNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("condition" , BNode),
            ("while_body", BNode),
        ))
    
    def compile(self):
        # info
        log__info("analyzing while loop...")

        # attrib
        attributes = self.getAttr()

class ForNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("for_var" , tuple),
            ("iterable", BNode),
            ("for_body", BNode),
        ))
    
    def compile(self):
        # info
        log__info("analyzing for loop...")

        # attrib
        attributes = self.getAttr()

class BlockNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            ("statements", tuple), 
        ))

class ContinueNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)

class BreakNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)

class YieldNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("expression", BNode),
        ))
    def compile(self):
        # info
        log__info("analyzing return statement...")

        # attrib
        attributes = self.getAttr()

class ReturnNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("expression", BNode),
        ))
    def compile(self):
        # info
        log__info("analyzing return statement...")

        # attrib
        attributes = self.getAttr()

        _dtype = None

        if  attributes["expression"] != None:
            _dtype = (attributes["expression"]
                            .compile())["datatype"]
        else:
            # default return
            _dtype = BBuiltinObject.Null

            # push const opcode
            self.putCode(ByteCodeChunk(
                line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = _dtype, obj = Null(None)
            ))

        # push return opcode
        self.putCode(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.RETURN
        ))

        # if incorrect return
        if  BNode.FUNC[-1][1] != _dtype:
            # throws error
            return errorHandler.throw__error(
                errorType.TYPE_ERROR, "function \"" + BNode.FUNC[-1][0].getSymbol() + "\" is declaired as \"" + BNode.FUNC[-1][1] + "\", got \"" + _dtype + "\"",
                trace__token(BNode.FUNC[-1][0])
            )
        else:
            # pop current function
            BNode.FUNC.pop()


class ExpressionStatementNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("expression", BNode),
        ))
    
    def compile(self):
        # info
        log__info("analyzing expression statement node...")

        # attrib
        attributes = self.getAttr()

class NoOpNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
    
    def compile(self):
        # info
        log__info("analyzing no operation...")

        # attrib
        attributes = self.getAttr()

class BinaryExpressionNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("opt", BToken) ,
            ("lhs", BNode ) ,
            ("rhs", BNode ) ,
        ))

    def compile(self):
        # info
        log__info("analyzing binary expression...")
        
        # attrib
        attributes = self.getAttr()

        # operator
        _opt:BToken = attributes["opt"]
        _opt_as_str = _opt.getSymbol()

        # right hand expression
        _rhs = (attributes["rhs"]
                .compile())

        # left hand expression
        _lhs = (attributes["lhs"]
                .compile())
        
        # push binary expr opcode
        self.putCode(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.BINARY_EXPR, operator = _opt_as_str
        ))

        # return datatype if expression
        return {"datatype": "Int"}

class UnaryExpressionNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib) 
        super().validate((
            # key, instance
            ("opt" , BToken ),
            ("expr", BNode  ),
        ))
    
    def compile(self):
        # info
        log__info("analyzing unary expression...")


class NullCheckAccessNode(BNode):
    def __init__(self, _path:str, _cont, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("object", BNode ),
            ("member", BToken),
        ))
    
    def compile(self):
        # info
        log__info("analyzing nullsafety access...")

class MemberAccessNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("object", BNode ),
            ("member", BToken),
        ))
    
    def compile(self):
        # info
        log__info("analyzing member access...")

        # attrib
        attributes = self.getAttr()

class CallNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("object"        , BNode ),
            ("arguments"     , tuple ),
            ("call_operator" , BToken),
        ))
    
    def compile(self):
        # info
        log__info("analyzing call expression...")

        # attrib
        attributes = self.getAttr()

class TypeNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("type", BToken),
        ))

    def compile(self):
        # info
        log__info("analyzing types...")

        # attrib
        attributes = self.getAttr()

        return "Null"

class ExtendedTypeNode(TypeNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("type"    , BToken   ),
            ("internal", TypeNode ),
        ))

    def compile(self):
        # info
        log__info("analyzing extended types...")

        # attrib
        attributes = self.getAttr()


class BooleanNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("object", BToken),
        ))
    
    def compile(self):
        # info
        log__info("analyzing boolean object...")
        
        # attrib
        attributes = self.getAttr()

        raw_object = attributes["object"]
        obj_as_str = raw_object.getSymbol()
        
class NullTypeNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("object", BToken),
        ))
    
    def compile(self):
        # info
        log__info("analyzing null object...")
        
        # attrib
        attributes = self.getAttr()

        raw_object = attributes["object"]
        obj_as_str = raw_object.getSymbol()

class ListNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("elements", tuple),
        ))
    
    def compile(self):
        # info
        log__info("analyzing list...")

        # attrib
        attributes = self.getAttr()

        # elements
        elements = attributes["elements"]

        for itm in elements[::-1]:
            itm.compile()
class ReferenceNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("reference", BToken),
        ))
    
    def compile(self):
        # info
        log__info("analyzing reference...")

        # attrib
        attributes = self.getAttr()

class SingleObjectNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("object", BToken),
        ))

    def convertTo(self, _type:type, _obj_symbol:str):
        data = None
        try:
            data = _type(_obj_symbol)
        except TypeError:
            return log__error(f"\"{_obj_symbol}\" is not \"{_type.__name__}\"")
        except ValueError:
            return log__error(f"\"{_obj_symbol}\" is not \"{_type.__name__}\"")
        return data

    def compile(self):
        # info
        log__info("analyzing builtin object...")

        # attrib
        attributes = self.getAttr()

        raw_object = attributes["object"]
        obj_as_str = raw_object.getSymbol()

        _lazy_eval = {
            BTokenType.INT : Int,
            BTokenType.FLT : Flt,
            BTokenType.STR : Str,
        }

        evaluator = _lazy_eval[raw_object.getType()]
        realDtype = { Int: int, Flt: float, Str: str }
        _obj = evaluator(self.convertTo(realDtype[evaluator], obj_as_str))

        # push const opcode
        self.putCode(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = obj_as_str, obj = _obj
        ))

        # return dataatype if expression
        return {"datatype": type(_obj).__name__}
