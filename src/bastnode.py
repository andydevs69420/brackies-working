from enum import Enum
from core.bobject import *
from bsymboltable import SymbolTable, SymbolType
from blogger import log__info, log__error
from bbytecode import OpCode, ByteCodeChunk
from bvirtualmachine import BVirtualMachine
from berrhandler import errorType, errorHandler
from btoken import BTokenType, BToken, trace__token


class BNode(object):

    LINE = 0
    @staticmethod
    def getLine():
        BNode.LINE += 2
        return (BNode.LINE - 2)

    def __init__(self, **_attrib):
        self.__attrib = _attrib
    
    def validate(self, _required:tuple[tuple]):
        for req in _required:
            if  req[0] not in self.__attrib.keys():
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! required key \"" + req[0] + "\" is not available!"
                )
            if  not isinstance(self.__attrib[req[0]], req[1]):
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! required type for key \"" + req[0] + "\" does not match. " + req[1].__name__ + " != " + type(self.__attrib[req[0]]).__name__
                )
        # success | valid flag
        return True

    def getPath(self):
        return self.__path
    
    def getCont(self):
        return self.__cont

    def getAttributes(self):
        return self.__attrib
    
    def analyze(self): pass
    def compile(self): pass


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

        attributes = self.getAttributes()

        # make new scope
        SymbolTable.new_scope()

        # load builtin opcode
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.LOAD_BUILTINS
        ))

        # compile statements
        for each_attrib in attributes["statements"]:
            each_attrib.compile()

        ############## make default return ##################
        memory_address = BVirtualMachine.push_to_heap(Null(None))
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = "null", mem_address = memory_address
        ))
        # return
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.RETURN
        ))
        ##############          end        ##################

        # end of scope
        SymbolTable.end_scope()

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
        attributes = self.getAttributes()

        # condition
        attributes["condition"].compile()

        BVirtualMachine.INSTRUCTIONS.append(None)
        current_line = self.getLine()
        byte_address = (len(BVirtualMachine.INSTRUCTIONS) - 1)

        # statement
        attributes["statement"].compile()

        # 
        BVirtualMachine.INSTRUCTIONS[byte_address] = ByteCodeChunk(
            line = current_line, opcode = OpCode.IF_ZERO_NULL_OR_FALSE, jump_loc = self.LINE + 2
        )

        # jump location 0
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.JUMP_TO, jump_loc = self.LINE
        ))
        
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
        attributes = self.getAttributes()

        # condition
        attributes["condition"].compile()

        BVirtualMachine.INSTRUCTIONS.append(None)
        _0current_line = self.getLine()
        _0byte_address = (len(BVirtualMachine.INSTRUCTIONS) - 1)

        # statement
        attributes["statement"].compile()
        # jump to end if
        BVirtualMachine.INSTRUCTIONS.append(None)
        _1current_line = self.getLine()
        _1byte_address = (len(BVirtualMachine.INSTRUCTIONS) - 1)
      
        # else line
        attributes["else_statement"].compile()
        # jump to end if
        BVirtualMachine.INSTRUCTIONS.append(None)
        _2current_line = self.getLine()
        _2byte_address = (len(BVirtualMachine.INSTRUCTIONS) - 1)


        # assign jump location on if statement
        # current jump 0
        BVirtualMachine.INSTRUCTIONS[_0byte_address] = ByteCodeChunk(
            line = _0current_line, opcode = OpCode.IF_ZERO_NULL_OR_FALSE, jump_loc = _1current_line + 2
        )

        # current jump 1
        BVirtualMachine.INSTRUCTIONS[_1byte_address] = ByteCodeChunk(
            line = _1current_line, opcode = OpCode.JUMP_TO, jump_loc = self.LINE
        )

        # current jump 1
        BVirtualMachine.INSTRUCTIONS[_2byte_address] = ByteCodeChunk(
            line = _2current_line, opcode = OpCode.JUMP_TO, jump_loc = self.LINE
        )
    
class NoOpNode(BNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
    
    def compile(self):
        # info
        log__info("analyzing no operation...")

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.NO_OP
        ))
        

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
        attributes = self.getAttributes()

        declairations = attributes["decl"]

        for each_dec in declairations:

            var_name, var_type = each_dec[0] # unpack
            var_name_as_string = var_name.getSymbol()

            if  SymbolTable.existL(var_name_as_string):

                _msg =  "\"" + var_name_as_string + "\" is already defined!" + "\n"
                _msg += "previous declairation of \"" + var_name_as_string + "\"..." + "\n"

                _occurance = SymbolTable.lookup(var_name_as_string)["token"]
                _msg += trace__token(_occurance) + "\n"

                _msg += "redefinition of \"" + var_name_as_string + "\"..." + "\n"
                _msg += trace__token(var_name)

                # throws error
                return errorHandler.throw__error(
                    errorType.NAME_ERROR, _msg
                )

            # compile dtype
            var_type = var_type.compile()

            if  each_dec[1] != None:
                # compile value
                each_dec[1].compile()
            else:
                symbol = None
                memory_address = None

                if  var_type == BBuiltinObject.Int:
                    symbol = "0"
                    memory_address = BVirtualMachine.push_to_heap(Int(0))
                elif  var_type == BBuiltinObject.Flt:
                    symbol = "0"
                    memory_address = BVirtualMachine.push_to_heap(Flt(0.0))
                elif  var_type == BBuiltinObject.Bool:
                    symbol = "false"
                    memory_address = BVirtualMachine.push_to_heap(Bool(False))
                else:
                    symbol = "null"
                    memory_address = BVirtualMachine.push_to_heap(Null(None))

                BVirtualMachine.push_instruction(ByteCodeChunk(
                    line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = symbol, mem_address = memory_address
                ))

            _address = SymbolTable.insert(
                symbol = var_name_as_string,
                token  = var_name,
                data_type = var_type,
                points_to = None,
            )

            BVirtualMachine.push_instruction(ByteCodeChunk(
                line = self.getLine(), opcode = OpCode.STORE_NAME, symbol = var_name_as_string, address = _address
            ))

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
        attributes = self.getAttributes()

        declairations = attributes["decl"]

        for each_dec in declairations:

            var_name, var_type = each_dec[0] # unpack
            var_name_as_string = var_name.getSymbol()

            if  SymbolTable.existL(var_name_as_string):

                _msg =  "\"" + var_name_as_string + "\" is already defined!" + "\n"
                _msg += "previous declairation of \"" + var_name_as_string + "\" below." + "\n"

                _occurance = SymbolTable.lookup(var_name_as_string)["token"]
                _msg += trace__token(_occurance) + "\n"

                _msg += "redefinition of \"" + var_name_as_string + "\" below." + "\n"
                _msg += trace__token(var_name)

                # throws error
                return errorHandler.throw__error(
                    errorType.NAME_ERROR, _msg
                )

            # compile dtype
            var_type = var_type.compile()

            if  each_dec[1] != None:
                # compile value
                each_dec[1].compile()
            else:
                symbol = None
                memory_address = None

                if  var_type == BBuiltinObject.Int:
                    symbol = "0"
                    memory_address = BVirtualMachine.push_to_heap(Int(0))
                elif  var_type == BBuiltinObject.Flt:
                    symbol = "0"
                    memory_address = BVirtualMachine.push_to_heap(Flt(0.0))
                elif  var_type == BBuiltinObject.Bool:
                    symbol = "false"
                    memory_address = BVirtualMachine.push_to_heap(Bool(False))
                else:
                    symbol = "null"
                    memory_address = BVirtualMachine.push_to_heap(Null(None))

                BVirtualMachine.push_instruction(ByteCodeChunk(
                    line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = symbol, mem_address = memory_address
                ))

            address = SymbolTable.insert(
                symbol = var_name_as_string,
                token  = var_name,
                data_type = var_type,
                points_to = None,
            )

            BVirtualMachine.push_instruction(ByteCodeChunk(
                line = self.getLine(), opcode = OpCode.STORE_LOCAL, symbol = var_name_as_string, address = address
            ))


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
        attributes = self.getAttributes()

        # exp
        expr = (attributes["expression"]
                .compile())
        
        # push pop instruction
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.POP_TOP
        ))

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

        attributes = self.getAttributes()

        attributes["rhs"].compile()
        attributes["lhs"].compile()
        
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.BINARY_EXPR, operator = attributes["opt"]
        ))

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
        attributes = self.getAttributes()

        # ref
        referenceL = attributes["reference"]
        ref_as_str = referenceL.getSymbol()

        prop = SymbolTable.lookup(ref_as_str)
        self_add = 0
        if  prop:
            self_add = prop["index"]
        
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_NAME, symbol = ref_as_str, raw = referenceL, self_address = self_add
        ))


############# OBJECT ###################
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
        attributes = self.getAttributes()

        # type
        bdata_type = attributes["type"]
        string_rep = bdata_type.getSymbol()

        if  string_rep in BRACKIES_TYPE and string_rep not in (BBuiltinObject.List, BBuiltinObject.Dict):
            return string_rep

        if  string_rep in (BBuiltinObject.List, BBuiltinObject.Dict):
            return errorHandler.throw__error(
                errorType.NAME_ERROR, "\"" + string_rep + "\" needs internal element type!",
                trace__token(bdata_type)
            )
        
        #TODO: add user defined types

        # throws error
        return errorHandler.throw__error(
            errorType.NAME_ERROR, "\"" + string_rep + "\" is not defined!",
            trace__token(bdata_type)
        )

class ExtendedTypeNode(TypeNode):
    def __init__(self, **_attrib):
        super().__init__(**_attrib)
        super().validate((
            # key, instance
            ("type"    , BToken),
            ("internal", tuple ),
        ))

    def compile(self):
        # info
        log__info("analyzing extended types...")

        # attrib
        attributes = self.getAttributes()

        # type
        bdata_type = attributes["type"]
        string_rep = bdata_type.getSymbol()

        # internal
        internal_type = attributes["internal"]

        # final type
        final_type = ""

        if  string_rep not in (BBuiltinObject.List, BBuiltinObject.Dict):
            # throws error
            return errorHandler.throw__error(
                errorType.NAME_ERROR, "\"" + string_rep + "\" does not needs internal type(s)!",
                trace__token(bdata_type)
            )
        
        final_type += string_rep

        if  string_rep == BBuiltinObject.List:
            if  len(internal_type) != 1:
                # throws error
                return errorHandler.throw__error(
                    errorType.NAME_ERROR, "\"" + string_rep + "\" must contains atleast 1 internal type!",
                    trace__token(bdata_type)
                )
        else:
            if  len(internal_type) != 2:
                # throws error
                return errorHandler.throw__error(
                    errorType.NAME_ERROR, "\"" + string_rep + "\" must contains atleast 2 internal type!",
                    trace__token(bdata_type)
                )
        
        if  len(internal_type) == 1:
            final_type += "_of_" + internal_type[0].compile()
        else:
            # dict
            final_type += "ionary" if (final_type + "ionary") == "Dictionary" else ""
            final_type += "_with a_key_type_of_" + internal_type[0].compile() + "_and_a_value_type_of_" + internal_type[1].compile()

        return final_type


############# OBJECT ###################
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


############# OBJECT ###################
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
        attributes = self.getAttributes()

        # obj
        _object = attributes["object"].compile()

        # member
        member = attributes["member"]
        member_as_str = member.getSymbol()

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_ATTRIB, symbol = member_as_str, raw = member
        ))



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

        


############# FUNCTION ################
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
        attributes = self.getAttributes()

        # save current instructions
        _current   = BVirtualMachine.INSTRUCTIONS
        _current_L = BNode.LINE
        BNode.LINE = 0
        BVirtualMachine.INSTRUCTIONS = []

        # function name
        func_name = attributes["func_name"]
        func_name_as_str = func_name.getSymbol()

        # return type
        return_type = (attributes["return_type"]
                        .compile())

        # make new scope
        SymbolTable.new_scope()

        # save scope
        _function_scope = SymbolTable.CURR

        # parameters
        parameters = attributes["parameters"]
        for each_param in parameters:
            _param, _param_type = each_param
            _param_as_string = _param.getSymbol()
            
            # data type
            _param_type_as_str = _param_type.compile()

            if  SymbolTable.lookup(_param_as_string):
                # throws error
                return errorHandler.throw__error(
                    errorType.NAME_ERROR, "parameter \"" + _param_as_string + "\" is already defined!",
                    trace__token(_param)
                )
            ######### STORE PARAMS ##############
            
            address = SymbolTable.insert(
                symbol = _param_as_string,
                token  = _param,
                data_type = _param_type_as_str,
                points_to = None,
            )

            BVirtualMachine.push_instruction(ByteCodeChunk(
                line = self.getLine(), opcode = OpCode.STORE_LOCAL, symbol = _param_as_string, address = address
            ))

        # body
        func_body = attributes["func_body"]
        for each_node in func_body:
            each_node.compile()
        
        ############## make default return ##################
        memory_address = BVirtualMachine.push_to_heap(Null(None))
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = "null", mem_address = memory_address
        ))
        # return
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.RETURN
        ))
        #######################  end  #######################

        # make new scope
        SymbolTable.end_scope()

        # function instructions
        _function_code = BVirtualMachine.INSTRUCTIONS

        BVirtualMachine.INSTRUCTIONS = _current
        BNode.LINE = _current_L

        if  SymbolTable.lookup(func_name_as_str):

            _msg =  "\"" + func_name_as_str + "\" is already defined!" + "\n"
            _msg += "previous declairation of \"" + func_name_as_str + "\" below." + "\n"

            _occurance = SymbolTable.lookup(func_name_as_str)["token"]
            _msg += trace__token(_occurance) + "\n"

            _msg += "redefinition of \"" + func_name_as_str + "\" below." + "\n"
            _msg += trace__token(func_name)

            # throws error
            return errorHandler.throw__error(
                errorType.NAME_ERROR, _msg,
            )

        ############## STORE FUNCTION ##############
        func_obj = Func(func_name_as_str, BrackiesCode(_function_code))
        f_memory_address = BVirtualMachine.push_to_heap(func_obj)

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = func_obj.toString().pyData(), mem_address = f_memory_address
        ))

        ######### STORE FUNCTION ##############
        f_address = SymbolTable.insert(
            symbol = func_name_as_str,
            token  = func_name,
            return_type = return_type,
            param_count = len(parameters),
            data_type   = BBuiltinObject.Func,
            points_to   = None,
            function_scope = _function_scope,
        )

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.STORE_FUNC, symbol = func_name_as_str, address = f_address
        ))

############# OBJECT ###################
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
        attributes = self.getAttributes()


        # evaluate right most arguments
        arguments = attributes["arguments"][::-1]
        for each_arg in arguments:
            each_arg.compile()

        # object
        callable_object = (attributes["object"]
                            .compile())

        # call_operator
        call_operator = attributes["call_operator"]

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.CALL, operator = call_operator, arg_count = len(arguments)
        ))


############# RETURN ###################
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
        attributes = self.getAttributes()

        expr = attributes["expression"]
        if  expr != None:
            expr.compile()
        else:
            # otherwise push null
            memory_address = BVirtualMachine.push_to_heap(Null(None))
            BVirtualMachine.push_instruction(ByteCodeChunk(
                line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = "null", mem_address = memory_address
            ))

        # return
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.RETURN,
        ))

############# OBJECT ###################
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
        attributes = self.getAttributes()

        raw_object = attributes["object"]
        obj_as_str = raw_object.getSymbol()

        _lazy_eval = {
            BTokenType.INT : Int,
            BTokenType.FLT : Flt,
            BTokenType.STR : Str,
        }

        evaluator = _lazy_eval[raw_object.getType()]
        realDtype = { Int: int, Flt: float, Str: str }
        memory_address = BVirtualMachine.push_to_heap(evaluator(self.convertTo(realDtype[evaluator], obj_as_str)))

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = obj_as_str, mem_address = memory_address
        ))


############# OBJECT ###################
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
        attributes = self.getAttributes()

        raw_object = attributes["object"]
        obj_as_str = raw_object.getSymbol()

        memory_address = BVirtualMachine.push_to_heap(Bool(True if obj_as_str == "true" else False))

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = obj_as_str, mem_address = memory_address
        ))
        
        
############# OBJECT ###################
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
        attributes = self.getAttributes()

        raw_object = attributes["object"]
        obj_as_str = raw_object.getSymbol()

        memory_address = BVirtualMachine.push_to_heap(Null(None))

        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.PUSH_CONST, symbol = obj_as_str, mem_address = memory_address
        ))

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
        attributes = self.getAttributes()

        # elements
        elements = attributes["elements"]

        for itm in elements[::-1]:
            itm.compile()
        
        BVirtualMachine.push_instruction(ByteCodeChunk(
            line = self.getLine(), opcode = OpCode.BUILD_LIST, length = len(elements)
        ))