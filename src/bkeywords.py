
from btoken import BToken


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
    KEYW_CONTINUE  = "continue"
    KEYW_BREAK     = "break"
    KEYW_YIELD     = "yield"
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