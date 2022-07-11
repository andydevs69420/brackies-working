from enum import Enum

__ALL__ = [ "BTokenType", "BToken" ]


NULLCHR = "\0"
BACKSPC = "\b"
TABCHAR = "\t"
NEWLINE = "\n"
CARRRET = "\r"
WHTESPC = " "

OPERATORS = ([
    "("  , ")"  , "["  , "]"  , "{" , "}" , 
    "?." , "."  , "!"  , "~"  , "++", "--", 
    "^^" , "*"  , "/"  , "%"  , "+" , "-" , 
    "<<" , ">>" , "<"  , "<=" , ">" , ">=", 
    "==", "!="  , "&"  , "^"  , "|" , "&&", 
    "||", "?"   , "="  , "*=" , "/=", "%=", 
    "+=", "-="  , "<<=", ">>=", "&=", "^=", 
    "|=", "..." , ","  , ":"  , ";"
])


class BTokenType(Enum):
    IDN = 0x00
    OTH = 0x01
    INT = 0x02
    FLT = 0x03
    STR = 0x04
    OPT = 0x05
    EOF = 0x06

class BToken(object):
    def __init__(self, _type:BTokenType, _symb:str, _post:tuple, _path:str, _content:str):
        self.__type = _type
        self.__symb = _symb
        self.__post = _post
        self.__path = _path
        self.__cont = _content

    def getType(self):
        return self.__type
    
    def getSymbol(self):
        return self.__symb
    
    def getPosition(self):
        return self.__post
    
    def getTokenPath(self):
        return self.__path

    def getTokenCont(self):
        return self.__cont

    def __str__(self):
        return f"{type(self).__name__}({self.__type.name}, \"{self.__symb}\", {self.__post})"


def trace__token( _token:BToken):

    lines = _token.getTokenCont().split("\n")
    posXY = _token.getPosition()
   
    trace = "[" + _token.getTokenPath() + ":" + str(posXY[2]) + ":" + str(posXY[0] + 1) + "]" + "\n\n"

    index = 1
    for line in lines:

        diffr = len(str(posXY[3])) - len(str(index))
        cline = (diffr * " ") + str(index) + " | "

        if  posXY[2] == posXY[3] and index == posXY[2]:
            trace += cline + line + "\n"
            trace += (len(cline) * " ")
            for idx in range(len(line)):
                if  idx >= posXY[0] and idx < posXY[1]:
                    trace += "^"
                else:
                    trace += " "
        
        if  posXY[2] != posXY[3] and index >= posXY[2] and index <= posXY[3]:
            trace += cline + " ~ " + line + "\n"

        index += 1

    # return new trace
    return trace