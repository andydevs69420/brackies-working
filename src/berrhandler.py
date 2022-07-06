from enum import Enum
from blogger import log__error

class errorType(Enum):
    SYNTAX_ERROR     = 0x01
    SEMANTIC_ERROR   = 0x02
    NAME_ERROR       = 0x03
    ATTRIBUTE_ERROR  = 0x04
    TYPE_ERROR       = 0x05
    STACK_OVERFLOW   = 0x06
    UNEXPECTED_ERROR = 0x067
class errorHandler:
    @staticmethod
    def throw__error(_error_type:errorType, _msg:str, _occurance:str=""):
        # split '_'
        _err = _error_type.name.split("_")
        _new = ""
        for each_word in _err:
            capital = each_word[0].capitalize()
            _new += capital + each_word[1:].lower()
        # write error message on stderr
        if  len(_occurance) <= 0:
            return log__error(_new + ":" + " " + _msg)
        # with occurance
        log__error(
            _new + ":" + " " + _msg +"\n"+
            _occurance
        )