from distutils.log import error
from bastnode import *
from blexer import BrackiesTokenizer
from btoken import BTokenType, trace__token
from berrhandler import errorType, errorHandler


class Keywords:
    
    KEYW_CLASS     = "class"
    KEYW_PUBLIC    = "public"
    KEYW_PRIVATE   = "private"
    KEYW_PROTECTED = "protected"
    KEYW_STATIC    = "static"
    KEYW_WITH      = "with"
    KEYW_FUNCTION  = "function"
    KEYW_VAR       = "var"
    KEYW_CONST     = "const"
    KEYW_LET       = "let"
    KEYW_RETURN    = "return"
    KEYW_IF        = "if"
    KEYW_ELSE      = "else"
    KEYW_SWITCH    = "switch"
    KEYW_CASE      = "case"
    KEYW_DEFAULT   = "default"
    KEYW_DO        = "do"
    KEYW_WHILE     = "while"
    KEYW_FOR       = "for"

    ###### ========== ######

    KEYW_TRUE  = "true"
    KEYW_FALSE = "false"
    KEYW_NULL  = "null"


    @staticmethod
    def isKeyword(_token:BToken):
        _attribs = Keywords.__dict__
        _keyword = [
            v
            for k, v in zip(_attribs.keys(), _attribs.values())
            if  k.startswith("KEYW")
        ]
        return (_token.getSymbol() in _keyword)


class ContextHelper(object):
    CTX_GLOBAL   = 0x01
    CTX_CLASS    = 0x02
    CTX_FUNCTION = 0x03
    CTX_LOCAL    = 0x04
    CTX_LOOP     = 0x05

    def __init__(self):
        self.__ctx_stack = []
    
    def push_ctx(self, _ctx:int):
        self.__ctx_stack.append(_ctx)
    
    def pop_ctx(self):
        if  len(self.__ctx_stack) <= 0:
            # throws error
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "fatal!!!! context is empty."
            )
        self.__ctx_stack.pop()
    
    def is_ctx(self, _ctx):
        return (_ctx in self.__ctx_stack)
    
    def is_ctx_restrict(self, _ctx):
        return (self.__ctx_stack[-1] == _ctx)

#################### BRACKIES PARSER ####################
## BEGIN
class BrackiesParser(BrackiesTokenizer):
    def __init__(self):
        super().__init__()
        self.__ctxh  = ContextHelper()
        self.__path  = None
        self.__cont  = None
        self.__ctokn = None
        self.__pAstt = None

    def __chk(self, _type_or_symbol:BTokenType or str):
        # validate!
        return (
            self.__ctokn.getType()   == _type_or_symbol or
            self.__ctokn.getSymbol() == _type_or_symbol
        )

    def __eat(self, _type_or_symbol:BTokenType or str):
        # check if match!
        if  self.__chk(_type_or_symbol):
            # get current token
            self.__ctokn = super().get_token()
            # return success flag
            return True
        
        # append
        _append = ""

        if  type(_type_or_symbol) == str:
            _append += ", try \"" + _type_or_symbol + "\""

        # otherwise error
        return errorHandler.throw__error(
            errorType.SYNTAX_ERROR, "unexpected token \"" + self.__ctokn.getSymbol() + "\"" + _append + "!",
            trace__token(self.__ctokn)
        )

    # parses input file
    def parse(self, _src:str, _raw_string:str):
        self.__path = _src
        self.__cont = _raw_string
        # initialize props
        super().feed_input(self.__path, self.__cont)

        # get current token
        self.__ctokn = super().get_token()

        # ast
        self.__pAstt = []

        # parse until token eof
        while not self.__chk(BTokenType.EOF):
            self.__pAstt.append(self.__p_source())
        
        # return ast 
        return self.__pAstt
        
    def __p_source(self):
        # push new context
        self.__ctxh.push_ctx(ContextHelper.CTX_GLOBAL)

        # source code
        _src_code = []
        
        # parse until eof
        while not self.__chk(BTokenType.EOF):
            _src_code.append(self.__p_statement())
            
        # eat type: "EOF"
        self.__eat(BTokenType.EOF)

        # pop context
        self.__ctxh.pop_ctx()

        # return new src node
        return SourceCodeNode(
            statements = tuple(_src_code)
        )
    
    ######### STATEMENTS ################

    def __p_statement(self):
        ################# DECLAIRATION ####################
        if  self.__chk(Keywords.KEYW_VAR):
            return self.__p_var_dec()
        # global const dec
        elif self.__chk(Keywords.KEYW_CONST):
            return self.__p_const_dec()
        # local dec
        elif self.__chk(Keywords.KEYW_LET):
            return self.__p_let_dec()
        # interface

        # class dec
        elif self.__chk(Keywords.KEYW_CLASS):
            return self.__p_class_dec()
        # class dec
        elif self.__chk(Keywords.KEYW_FUNCTION):
            return self.__p_function_dec()
        ################# COMPOUND  ####################
        elif self.__chk(Keywords.KEYW_IF):
            return self.__p_if_stmnt()
        elif self.__chk(Keywords.KEYW_SWITCH):
            return self.__p_switch_stmnt()
        # iteration
        elif self.__chk(Keywords.KEYW_WHILE):
            return self.__p_while_stmnt()
        elif self.__chk(Keywords.KEYW_FOR):
            return self.__p_for_stmnt()
        elif self.__chk(BTokenType.OPT) and self.__chk("{"):
            return self.__p_block()
        ################################################
        elif self.__chk(Keywords.KEYW_RETURN):
            return self.__p_return()
        ################# ITERATION ####################
        # expr
        return self.__p_expresion_statement()
    
    ###### VARIABLE DEC ######
    # var
    def __p_var_dec(self):
        # var dec is only in global context
        if  not self.__ctxh.is_ctx_restrict(ContextHelper.CTX_GLOBAL):
            # throws error
            return errorHandler.throw__error(
                errorType.SEMANTIC_ERROR, "global variable declairation should be in global scope only!",
                trace__token(self.__ctokn)
            )

        # eat keyw: "var"
        self.__eat(Keywords.KEYW_VAR)

        # declairations
        _decl = self.declairations()

        # eat opt: ";"
        self.__eat(";")

        # return variable dec node
        return GlobalVariableNode(
            decl = _decl
        )
    
    # const
    def __p_const_dec(self):
        # const dec is only in global context
        if  not self.__ctxh.is_ctx_restrict(ContextHelper.CTX_GLOBAL):
            # throws error
            return errorHandler.throw__error(
                errorType.SEMANTIC_ERROR, "constant variable declairation should be in global scope only!",
                trace__token(self.__ctokn)
            )

        # eat keyw: "const"
        self.__eat(Keywords.KEYW_CONST)

        # declairations
        _decl = self.declairations()

        # eat opt: ";"
        self.__eat(";")

        # return const variable dec node
        return ConstVariableNode(
            decl = _decl
        )
    
    # let
    def __p_let_dec(self):
        # const dec is only in global context
        if  not self.__ctxh.is_ctx(ContextHelper.CTX_LOCAL):
            # throws error
            return errorHandler.throw__error(
                errorType.SEMANTIC_ERROR, "local variable declairation is not allowed here!",
                trace__token(self.__ctokn)
            )

        # eat keyw: "let"
        self.__eat(Keywords.KEYW_LET)

        # declairations
        _decl = self.declairations()

        # eat opt: ";"
        self.__eat(";")

        # return const variable dec node
        return LocalVariableNode(
            decl = _decl
        )
    
    def declairations(self):
        # declist
        _declist = []

        # first dec!! required.
        _dec0 = self.dec_pair()
        
        # append first
        _declist.append(_dec0)

        while self.__chk(","):

            # eat opt: ","
            _opt = self.__ctokn
            self.__eat(",")

            if  not self.__chk(BTokenType.IDN):
                # error if not identifier
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "remove symbol \"" + _opt.getSymbol() + "\" or make another declairation.",
                    trace__token(_opt)
                )

            # next
            _decN = self.dec_pair()

            # append nth
            _declist.append(_decN)
        
        # dec list
        return tuple(_declist)

            
    
    def dec_pair(self):
        # name
        _name = self.__p_identifier_non_ref()

        # eat opt: ":"
        self.__eat(":")

        # type
        _type = self.__p_brackies_type()

        _var_and_type = (_name, _type)
        
        if  not self.__chk("="):
            return (_var_and_type, None)

        # eat opt: "="
        _optr = self.__ctokn
        self.__eat("=")

        # value
        _expr = self.__p_expression()
        
        # validate
        if  not _expr:
            # throws error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "missing right hand value after \"" + _optr.getSymbol() + "\"!",
                trace__token(_optr)
            )
        # return pair
        return (_var_and_type, _expr)
    
    ####### TYPE DEC #########
    
    def __p_class_dec(self):
        # class dec is only in global context
        if  not self.__ctxh.is_ctx_restrict(ContextHelper.CTX_GLOBAL):
            # throws error
            return errorHandler.throw__error(
                errorType.SEMANTIC_ERROR, "class declairation must be in global scope!",
                trace__token(self.__ctokn)
            )

        # push new context
        self.__ctxh.push_ctx(ContextHelper.CTX_CLASS)
        
        # eat keyw: "class"
        self.__eat(Keywords.KEYW_CLASS)

        # class name
        _class_name = self.__p_identifier_non_ref()

        _is_extended = False
        _super_class = None

        # if extended
        if  self.__chk(Keywords.KEYW_WITH):
            # update flag
            _is_extended = True

            # eat keyw: "with"
            self.__eat(Keywords.KEYW_WITH)

            # super class
            _super_class = self.__p_identifier_non_ref()

        # class body
        _class_body = self.class_body()

        # pop context
        self.__ctxh.pop_ctx()

        ############### ==================== ###############

        if  not _is_extended:
            # return class dec node
            return ClassNode(
                class_name = _class_name,
                class_body = _class_body,
            )
        else:
            # extended class node
            return ExtendedClassNode(
                class_name  = _class_name ,
                super_class = _super_class,
                class_body  = _class_body ,
            )
    

    def class_body(self):

        _class_member = []
        
        # eat opt: "{"
        self.__eat("{")

        _mem0 = self.__p_member_accessibility()
        
        while _mem0:
            _class_member.append(_mem0)
            _mem0 = self.__p_member_accessibility()

        # eat opt: "}"
        self.__eat("}")

        # list of member
        return tuple(_class_member)
    
    def __p_member_accessibility(self):

        if  self.__chk(Keywords.KEYW_PROTECTED):
            # eat keyw: "protected"
            self.__eat(Keywords.KEYW_PROTECTED)
            return AccessModNode(
                access_modifier = AccessModifier.PROTECTED,
                prop = self.other_accessibility()
            )
        elif  self.__chk(Keywords.KEYW_PRIVATE):
            # eat keyw: "private"
            self.__eat(Keywords.KEYW_PRIVATE)
            return AccessModNode(
                access_modifier = AccessModifier.PRIVATE,
                prop = self.other_accessibility()
            )
        elif self.__chk(Keywords.KEYW_PUBLIC):
            # eat keyw: "public"
            self.__eat(Keywords.KEYW_PUBLIC)
            return AccessModNode(
                access_modifier = AccessModifier.PUBLIC,
                prop = self.other_accessibility()
            )
        
        return self.other_accessibility()
    
    def other_accessibility(self):

        if  self.__chk(Keywords.KEYW_STATIC):
            # eat keyw: "static"
            self.__eat(Keywords.KEYW_STATIC)
            return StaticNode(static_prop = self.allowed_in_class())
        
        return self.allowed_in_class()
    
    def allowed_in_class(self):

        if  Keywords.isKeyword(self.__ctokn) and self.__chk(Keywords.KEYW_FUNCTION):
            return self.__p_function_dec()
        elif self.__chk(BTokenType.IDN):
            return self.class_var()
        
        return None
    
    def class_var(self):
        
        _decl = self.class_declairations()

        # eat opt: ";"
        self.__eat(";")

        # return class var node
        return ClassVarNode(decl = _decl)
    
    def class_declairations(self):
        # declist
        _declist = []

        # first dec!! required.
        _dec0 = self.class_dec_pair()
        
        # append first
        _declist.append(_dec0)

        while self.__chk(","):

            # eat opt: ","
            _opt = self.__ctokn
            self.__eat(",")

            if  not self.__chk(BTokenType.IDN):
                # error if not identifier
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "remove symbol \"" + _opt.getSymbol() + "\" or make another declairation.",
                    trace__token(_opt)
                )

            # next
            _decN = self.class_dec_pair()

            # append nth
            _declist.append(_decN)
        
        return tuple(_declist)

    def class_dec_pair(self):
        # name
        _name = self.__p_identifier_non_ref()

        # eat opt: ":"
        self.__eat(":")

        # type
        _type = self.__p_brackies_type()

        _var_and_type = (_name, _type)
        
        if  not self.__chk("="):
            return (_var_and_type, None)

        # eat opt: "="
        _optr = self.__ctokn
        self.__eat("=")

        # value
        _expr = self.__p_expression()
        
        # validate
        if  not _expr:
            # throws error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "missing right hand value after \"" + _optr.getSymbol() + "\"!",
                trace__token(_optr)
            )
        # return pair
        return (_var_and_type, _expr)
    
    ###### FUNCTION DEC ######
    def __p_function_dec(self):
        # function dec is only in global context
        if  not (self.__ctxh.is_ctx_restrict(ContextHelper.CTX_GLOBAL) or self.__ctxh.is_ctx_restrict(ContextHelper.CTX_CLASS)):
            # throws error
            return errorHandler.throw__error(
                errorType.SEMANTIC_ERROR, "function declairation must be in global scope!",
                trace__token(self.__ctokn)
            )
        
        # push new context
        self.__ctxh.push_ctx(ContextHelper.CTX_FUNCTION)

        # eat keyw: "function"
        self.__eat(Keywords.KEYW_FUNCTION)

        # function name
        _func_name = self.__p_identifier_non_ref()

        # eat opt: ":"
        self.__eat(":")

        # type
        _return_type = self.__p_brackies_type()

        # params
        _params = self.func_param_list()

        # funcbody 
        _func_body = self.func_body()

        # pop context
        self.__ctxh.pop_ctx()

        # return function
        return FunctionNode(
            func_name   = _func_name  ,
            return_type = _return_type,
            parameters  = _params     ,
            func_body   = _func_body  ,
        )
    
    def func_param_list(self):

        _params = []

        # eat opt: "("
        self.__eat("(")

        _param0 = self.func_param()

        if  _param0:
            # append first param
            _params.append(_param0)

        while self.__chk(","):
            # eat opt: ","
            _opt = self.__ctokn
            self.__eat(",")

            _paramN = self.func_param()

            if  not _paramN:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "remove symbol \"" + _opt.getSymbol() + "\" or make another declairation.",
                    trace__token(_opt)
                )
            
            # append nth param
            _params.append(_paramN)

        # eat opt: ")"
        self.__eat(")")

        # return params
        return tuple(_params)
    
    def func_param(self):

        # check if has parameter
        if  not self.__chk(BTokenType.IDN):
            return

        # eat tpye: "idn"
        _param = self.__p_identifier_non_ref()

        # eat opt: ":"
        self.__eat(":")

        # type
        _type = self.__p_brackies_type()

        # return pair
        return (_param, _type)
    

    def func_body(self):
        # push new context
        self.__ctxh.push_ctx(ContextHelper.CTX_LOCAL)

        _class_member = []
        
        # eat opt: "{"
        self.__eat("{")

        _mem0 = self.__p_statement()
        
        while _mem0:
            _class_member.append(_mem0)
            _mem0 = self.__p_statement()

        # eat opt: "}"
        self.__eat("}")

        # pop context
        self.__ctxh.pop_ctx()

        # list of member
        return tuple(_class_member)
    ############### COMPOUND ################
    def __p_if_stmnt(self):

        # eat keyw: "if"
        self.__eat(Keywords.KEYW_IF)
        
        # eat opt: "("
        self.__eat("(")

        _condition = self.__p_expression()

        # eat opt: ")"
        self.__eat(")")

        _statement = self.__p_statement()

        if  not self.__chk(Keywords.KEYW_ELSE):
            # returnh if node
            return IfNode(
                condition = _condition,
                statement = _statement
            )

        # eat keyw: "else"
        self.__eat(Keywords.KEYW_ELSE)
        
        _else_statement = self.__p_statement()
        
        # return if else node
        return IfElseNode(
            condition = _condition,
            statement = _statement,
            else_statement = _else_statement
        )
    
    ###### SWITCH STATEMENT     #####
    def __p_switch_stmnt(self):
        # eat keyw: "switch"
        self.__eat(Keywords.KEYW_SWITCH)

        # eat opt: "("
        _opt = self.__ctokn
        self.__eat("(")

        _expr = self.__p_expression()
        if  not _expr:
            # throws error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "an expression is expected after symbol \"" + _opt.getSymbol() + "\".",
                trace__token(_opt)
            )

        # eat opt: ")"
        self.__eat(")")

        _switch_body = self.switch_body()

        return
    
    def switch_body(self):

        _switch_body = []

        # eat opt: "{"
        self.__eat("{")

        while self.__chk(Keywords.KEYW_CASE):
            _switch_body.append(self.switch_case())
        
        if  self.__chk(Keywords.KEYW_DEFAULT):

            # eat keyw: "default"
            self.__eat(Keywords.KEYW_DEFAULT)

            # eat opt: ":"
            self.__eat(":")

            _switch_body.append((None, self.__p_statement())) 
        
        # eat opt: "}"
        self.__eat("}")
        
        return tuple(_switch_body)
    
    def switch_case(self):
        
        # eat keyw: "case"
        _keyw = self.__ctokn
        self.__eat(Keywords.KEYW_CASE)

        _matches = []

        _match0 = self.__p_expression()
        if  not _match0:
            # throws error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "switch cases requires atleast 1 expression.",
                trace__token(_keyw)
            )

        _matches.append(_match0)
        while self.__chk(","):
            # eat opt: ","
            _opt = self.__ctokn
            self.__eat(",")

            _matchN = self.__p_expression()
            if  not _matchN:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "remove symbol \"" + _opt.getSymbol() + "\" or add another expression.",
                    trace__token(_opt)
                )

            _matches.append(_matchN)

        # eat opt: ":"
        self.__eat(":")

        # match, ifmatch
        return (_matches, self.__p_statement())

    ###### WHILE STATEMENT      #####
    def __p_while_stmnt(self):
        # push loop context
        self.__ctxh.push_ctx(ContextHelper.CTX_LOOP)

        # eat keyw: "while"
        self.__eat(Keywords.KEYW_WHILE)

        _opt = self.__ctokn
        # eat opt: "("
        self.__eat("(")

        _condition = self.__p_expression()
        if  not _condition:
            # throws error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "expects condition after \"" + _opt.getSymbol() + "\"!",
                trace__token(_opt)
            )

        # eat opt: ")"
        self.__eat(")")

        # while body
        _while_body = self.__p_statement()

        # pop loop context
        self.__ctxh.pop_ctx()
        
        return WhileNode(
            condition  = _condition,
            while_body = _while_body
        )

    ###### FOR STATEMENT        #####
    def __p_for_stmnt(self):
        # push loop context
        self.__ctxh.push_ctx(ContextHelper.CTX_LOOP)

        # eat keyw: "for"
        self.__eat(Keywords.KEYW_FOR)

        # eat opt: "("
        self.__eat("(")
        
        _var = self.for_var()

        # eat opt: "..."
        self.__eat("...")
        
        _iterable = self.__p_expression()

        # eat opt: ")"
        self.__eat(")")

        _for_body = self.__p_statement()

        # pop loop context
        self.__ctxh.pop_ctx()

        return ForNode(
            for_var  = _var,
            iterable = _iterable,
            for_body = _for_body
        )
    
    def for_var(self):

        _var_name = self.__p_identifier_non_ref()

        # eat opt: ":"
        self.__eat(":")

        _var_type = self.__p_brackies_type()

        return tuple([_var_name, _var_type])
    

    def __p_block(self):
        # push local ctx
        self.__ctxh.push_ctx(ContextHelper.CTX_LOCAL)

        _statement_list = []

        # eat opt: "{"
        self.__eat("{")

        _statement = self.__p_statement()
        
        while _statement:
            _statement_list.append(_statement)
            _statement = self.__p_statement()

        # eat opt: "}"
        self.__eat("}")

        # pop local
        self.__ctxh.pop_ctx()

        return BlockNode(
            statements = tuple(_statement_list)
        )
    
    ###### RETURN STATEMENT     #####
    def __p_return(self):

        if  not self.__ctxh.is_ctx(ContextHelper.CTX_FUNCTION):
            # throws error
            return errorHandler.throw__error(
                errorType.SEMANTIC_ERROR, "invalid \"" + self.__ctokn.getSymbol() + "\" statement outside function scope!",
                trace__token(self.__ctokn)
            )
        
        # eat keyw: "return"
        self.__eat(Keywords.KEYW_RETURN)

        # return expr
        _expr = self.__p_expression()
        
        # eat opt: ";"
        self.__eat(";")

        # return
        return ReturnNode(expression = _expr)
    
    ###### EXPRESSION STATEMENT #####
    def __p_expresion_statement(self):

        expr = self.__p_expression()

        if  expr:
            # eat opt: ";"
            self.__eat(";")
            return ExpressionStatementNode(expression = expr)
        elif self.__chk(";"):
            while self.__chk(";"):
                self.__eat(";")
            # return no operation
            return NoOpNode()
        else:
            return expr

    ######### BINARY EXPRESSION #########

    def __p_expression(self):
        return self.__p_logical_expression()
    
    def __p_logical_expression(self):
        # node or left hand expr
        node_or_lhs = self.__p_equality_expression()

        # check if null | None
        if  not node_or_lhs:
            return node_or_lhs
        
        # while opt: "&&" | "||"
        while self.__chk("&&") or self.__chk("||"):
            # copy operator
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())
            
            # rhs(right hand expr)
            _rhs = self.__p_logical_expression()

            # verify rhs
            if  not _rhs:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "missing right hand expression for operator \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            
            # update node
            node_or_lhs = BinaryExpressionNode(
                opt = _opt,
                lhs = node_or_lhs,
                rhs = _rhs,
            )

        # return current node
        return node_or_lhs

    def __p_equality_expression(self):
        # node or left hand expr
        node_or_lhs = self.__p_bitwise_expression()

        # check if null | None
        if  not node_or_lhs:
            return node_or_lhs
        
        # while opt: "==" | "!="
        while self.__chk("==") or self.__chk("!="):
            # copy operator
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())
            
            # rhs(right hand expr)
            _rhs = self.__p_equality_expression()

            # verify rhs
            if  not _rhs:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "missing right hand expression for operator \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            
            # update node
            node_or_lhs = BinaryExpressionNode(
                opt = _opt,
                lhs = node_or_lhs,
                rhs = _rhs,
            )

        # return current node
        return node_or_lhs

    def __p_bitwise_expression(self):
        # node or left hand expr
        node_or_lhs = self.__p_relational_expression()

        # check if null | None
        if  not node_or_lhs:
            return node_or_lhs
        
        # while opt: "&" | "^" | "|"
        while self.__chk("&") or self.__chk("^") or self.__chk("|"):
            # copy operator
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())
            
            # rhs(right hand expr)
            _rhs = self.__p_bitwise_expression()

            # verify rhs
            if  not _rhs:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "missing right hand expression for operator \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            
            # update node
            node_or_lhs = BinaryExpressionNode(
                opt = _opt,
                lhs = node_or_lhs,
                rhs = _rhs,
            )

        # return current node
        return node_or_lhs

    def __p_relational_expression(self):
        # node or left hand expr
        node_or_lhs = self.__p_shift_expression()

        # check if null | None
        if  not node_or_lhs:
            return node_or_lhs
        
        # while opt: "<" | "<=" | ">" | ">="
        while self.__chk("<") or self.__chk("<=") or self.__chk(">") or self.__chk(">="):
            # copy operator
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())
            
            # rhs(right hand expr)
            _rhs = self.__p_relational_expression()

            # verify rhs
            if  not _rhs:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "missing right hand expression for operator \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            
            # update node
            node_or_lhs = BinaryExpressionNode(
                opt = _opt,
                lhs = node_or_lhs,
                rhs = _rhs,
            )

        # return current node
        return node_or_lhs

    def __p_shift_expression(self):
        # node or left hand expr
        node_or_lhs = self.__p_addition_or_subtract()

        # check if null | None
        if  not node_or_lhs:
            return node_or_lhs
        
        # while opt: "<<" | ">>"
        while self.__chk("<<") or self.__chk(">>"):
            # copy operator
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())
            
            # rhs(right hand expr)
            _rhs = self.__p_shift_expression()

            # verify rhs
            if  not _rhs:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "missing right hand expression for operator \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            
            # update node
            node_or_lhs = BinaryExpressionNode(
                opt = _opt,
                lhs = node_or_lhs,
                rhs = _rhs,
            )

        # return current node
        return node_or_lhs

    def __p_addition_or_subtract(self):
        # node or left hand expr
        node_or_lhs = self.__p_mult_or_div_or_modulo()

        # check if null | None
        if  not node_or_lhs:
            return node_or_lhs
        
        # while opt: "+" | "-"
        while self.__chk("+") or self.__chk("-"):
            # copy operator
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())
            
            # rhs(right hand expr)
            _rhs = self.__p_addition_or_subtract()

            # verify rhs
            if  not _rhs:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "missing right hand expression for operator \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            
            # update node
            node_or_lhs = BinaryExpressionNode(
                opt = _opt,
                lhs = node_or_lhs,
                rhs = _rhs,
            )

        # return current node
        return node_or_lhs

    def __p_mult_or_div_or_modulo(self):
        # node or left hand expr
        node_or_lhs = self.__p_unary_expression()
        # check if null | None
        if  not node_or_lhs:
            return node_or_lhs
        
        # while opt: "*" | "/" | "%"
        while self.__chk("*") or self.__chk("/") or self.__chk("%"):
            # copy operator
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())
            
            # rhs(right hand expr)
            _rhs = self.__p_mult_or_div_or_modulo()

            # verify rhs
            if  not _rhs:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "missing right hand expression for operator \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            
            # update node
            node_or_lhs = BinaryExpressionNode(
                opt = _opt,
                lhs = node_or_lhs,
                rhs = _rhs,
            )

        # return current node
        return node_or_lhs
    
    ######### UNARY EXPRESSION #########

    def __p_unary_expression(self):
        # object or node
        if  (
            self.__chk( "~"  ) or self.__chk( "!"   ) or 
            self.__chk( "+"  ) or self.__chk( "-"   ) or 
            self.__chk( "++" ) or self.__chk( "--"  )
        ):
            # eat opt: "~" | "!" | "+" | "-" | "++" | "--"
            _opt = self.__ctokn
            self.__eat(_opt.getSymbol())

            # expr
            _exp = self.__p_unary_expression()

            # verify rhs
            if  not _exp:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "an expression is expected after \"" + _opt.getSymbol() + "\" symbol!",
                    trace__token(_opt)
                )
            # returns unary expr node
            return UnaryExpressionNode(
                opt  = _opt,
                expr = _exp,
            )
        
        # otherwise member or call
        return self.__p_member_or_call()
    
    ######### MEMBER ACCESS OR CALL ########

    def __p_member_or_call(self):
        # object or node
        obj_or_node = self.__p_parenthesised()
        if  not obj_or_node:
            return obj_or_node
        
        # parse while "?." | "." | "("
        while self.__chk("?.") or self.__chk(".") or self.__chk("[") or self.__chk("("):

            # null check access
            if  self.__chk("?."):

                # eat opt: "?."
                self.__eat("?.")
                
                # id | member
                _member = self.__p_identifier_non_ref()

                obj_or_node = NullCheckAccessNode(
                    object  =   obj_or_node ,
                    member  =   _member     ,
                )
            
            elif self.__chk("."):

                # eat opt: "."
                self.__eat(".")
                
                # id | member
                _member = self.__p_identifier_non_ref()

                obj_or_node = MemberAccessNode(
                    object  =   obj_or_node ,
                    member  =   _member     ,
                )
            elif self.__chk("("):
                
                # eat opt: "("
                _lparen = self.__ctokn
                self.__eat("(")

                _arguments = self.call_arguments()

                # eat opt: ")"
                _rparen = self.__ctokn
                self.__eat(")")
        
                startX = _lparen.getPosition()[0]
                endX   = _rparen.getPosition()[1]
                
                startY = _lparen.getPosition()[2]
                endY   = _rparen.getPosition()[3]

                _symbol = _lparen.getTokenCont().split('\n')[startY-1][startX:endX]

                _new_token = BToken(
                    BTokenType.OPT, _symbol, (startX, endX, startY, endY),
                    _lparen.getTokenPath(), _lparen.getTokenCont()
                )

                obj_or_node = CallNode(
                    object     =  obj_or_node ,
                    arguments  =  _arguments  ,
                    call_operator =  _new_token
                )

        # return curent node
        return obj_or_node
    
    def call_arguments(self):
        # arg list
        _args = []

        _arg0 = self.__p_expression()
        if  not _arg0:
            return tuple(_args)
        
        _args.append(_arg0)

        while self.__chk(","):
            
            # eat opt: ","
            _opt = self.__ctokn
            self.__eat(",")

            _argN = self.__p_expression()
            if  not _argN:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "remove symbol \"" + _opt.getSymbol() + "\" or make another expression.",
                    trace__token(_opt)
                )
            
            _args.append(_argN)

        # return args list
        return tuple(_args)

    
    def __p_parenthesised(self):
        if  self.__chk("("):
            _opt = self.__ctokn
            # eat opt: "("
            self.__eat("(")
            expr = self.__p_expression()
            # check
            if  not expr:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "empty expression after \"" + _opt.getSymbol() + "\"!",
                    trace__token(_opt)
                )
            # eat opt: ")"
            self.__eat(")")

            # return expression
            return expr
        else:
            # otherwise return datatype
            return self.__p_other_type()
    
    ######### OTHER TYPE #########

    def __p_other_type(self):
        # current node
        node_or_none = self.__p_ref_or_datatype()
        if node_or_none:
            return node_or_none
        
        # otherwise other type?
        # bool true
        if  self.__chk(Keywords.KEYW_TRUE) or self.__chk(Keywords.KEYW_FALSE):
            return self.__p_boolean()
        elif self.__chk(Keywords.KEYW_NULL):
            return self.__p_nulltype()
        elif self.__chk("["):
            return self.__p_list()
        
        return None
    
    def __p_boolean(self):
        # copy
        obj = self.__ctokn
        # eat type: "IDN"
        self.__eat(BTokenType.IDN)
        # return new single obj node
        return BooleanNode(
            object = obj,
        )

    def __p_nulltype(self):
        # copy
        obj = self.__ctokn
        # eat type: "IDN"
        self.__eat(BTokenType.IDN)
        # return new single obj node
        return NullTypeNode(
            object = obj
        )
    

    ######### OTHER TYPE ########

    def __p_list(self):

        # eat opt: "["
        self.__eat("[")

        _elements = self.list_element()

        # eat opt: "]"
        self.__eat("]")

        return ListNode(
            elements = _elements
        )
    
    def list_element(self):

        _elements = []

        _elem0 = self.__p_expression()
        if  not _elem0:
            return tuple(_elements)
        
        _elements.append(_elem0)
        
        while self.__chk(","):
            # copy
            _opt = self.__ctokn
            self.__eat(",")

            _elemN = self.__p_expression()
            if  not _elemN:
                # throws error
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "remove symbol \"" + _opt.getSymbol() + "\" or add another element.",
                    trace__token(_opt)
                )
            
            _elements.append(_elemN)

        return tuple(_elements)

    ######### DATATYPES #########

    def __p_ref_or_datatype(self):
        # identifier
        if  self.__chk(BTokenType.IDN) and not (self.__chk(Keywords.KEYW_TRUE) or self.__chk(Keywords.KEYW_FALSE) or self.__chk(Keywords.KEYW_NULL)):
            return self.__p_idn()
        # integer other
        if  self.__chk(BTokenType.OTH):
            return self.__p_oth()
        if  self.__chk(BTokenType.INT):
            return self.__p_int()
        # float
        if  self.__chk(BTokenType.FLT):
            return self.__p_flt()
        # string
        if  self.__chk(BTokenType.STR):
            return self.__p_str()
        
        return None
    
    def __p_idn(self):
        if  self.__chk(BTokenType.IDN) and Keywords.isKeyword(self.__ctokn):
            # throws error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "unexpected keyword \"" + self.__ctokn.getSymbol() + "\"!",
                trace__token(self.__ctokn)
            )
        # copy
        obj = self.__ctokn
        # eat type: "IDN"
        self.__eat(BTokenType.IDN)
        # return reference 
        return ReferenceNode(
            reference = obj
        )

    def __p_oth(self):
        # copy
        obj = self.__ctokn
        # eat type: "INT"
        self.__eat(BTokenType.OTH)
        # return new single obj node
        return SingleObjectNode(
            object = obj
        )

    def __p_int(self):
        # copy
        obj = self.__ctokn
        # eat type: "INT"
        self.__eat(BTokenType.INT)
        # return new single obj node
        return SingleObjectNode(
            object = obj
        )

    def __p_flt(self):
        # copy
        obj = self.__ctokn
        # eat type: "FLT"
        self.__eat(BTokenType.FLT)
        # return new single obj node
        return SingleObjectNode(
            object = obj
        )

    def __p_str(self):
        # copy
        obj = self.__ctokn
        # eat type: "STR"
        self.__eat(BTokenType.STR)
        # return new single obj node
        return SingleObjectNode(
            object = obj
        )
    
    ###### SUPPORTED TYPES ########

    def __p_brackies_type(self):
    
        # eat type: IDN
        _type = self.__ctokn
        self.__eat(BTokenType.IDN)

        if  not self.__chk("["):
            # return type node
            return TypeNode(
                type = _type
            )

        # eat opt: "["
        self.__eat("[")

        _internal_type = self.__p_brackies_type()
    
        # eat opt: "]"
        self.__eat("]")

        # return extended type
        return ExtendedTypeNode(
            type     = _type,
            internal = _internal_type
        )
    
    
    ###### INDIVIDUAL RAW ######

    def __p_identifier_non_ref(self):
        if  self.__chk(BTokenType.IDN) and Keywords.isKeyword(self.__ctokn):
            # throws error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "unexpected keyword \"" + self.__ctokn.getSymbol() + "\"!",
                trace__token(self.__ctokn)
            )
        # copy
        obj = self.__ctokn
        # eat type: "IDN"
        self.__eat(BTokenType.IDN)
        # return new single obj node
        return obj
## END





class BrackiesMain(BrackiesParser):
    def __init__(self):
        super().__init__()

    def parse(self, _path, _cont):
        return super().parse(_path, _cont)

