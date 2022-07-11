from enum import Enum
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
    @staticmethod
    def getLine():
        BNode.LINE += 2
        return (BNode.LINE - 2)

    def __init__(self, **_attrib):
        self.__attr = _attrib
    
    def validate(self, _required:tuple[tuple]):
        for req in _required:
            if  req[0] not in self.__attr.keys():
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! required key \"" + req[0] + "\" is not available!"
                )
            if  not isinstance(self.__attr[req[0]], req[1]):
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! required type for key \"" + req[0] + "\" does not match. " + req[1].__name__ + " != " + type(self.__attr[req[0]]).__name__
                )
        # success | valid flag
        return True

    def getPath(self):return self.__path
    def getCont(self):return self.__cont
    def getAttr(self):return self.__attr
    def analyze(self):
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

class StaticNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            ("static_prop", BNode),
        ))
        

class ClassVarNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            ("decl", tuple),
        ))

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
        obj = evaluator(self.convertTo(realDtype[evaluator], obj_as_str))
