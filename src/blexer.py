from btoken import *
from bstack import BStack 
from berrhandler import errorType, errorHandler

#################### BRACKIES BASE CLASS ####################
## BEGIN
class Brackies(object):
    def __init__(self):
        super().__init__()
## END


#################### BRACKIES TOKENIZER ####################
## BEGIN
class BrackiesTokenizer(Brackies):
    def __init__(self):
        super().__init__()
        self.__STACK = BStack()
        self.__stack = BStack()
        self.__iseof = None
        self.__path  = None
        self.__cont  = None
        self.__clook = None
        self.__index = None
        self.__cline = 1
        self.__ccolm = 1

    def __next_index(self):
        global NEWLINE
        # check line and column
        if  self.__clook == NEWLINE:
            self.__cline += 1
            self.__ccolm  = 1
        else:
            self.__ccolm += 1
        # increase index
        self.__index += 1
        # forwarding
        if  self.__index < len(self.__cont):
            self.__iseof = False
            self.__clook = self.__cont[self.__index]
        else:
            self.__iseof = True
            self.__clook = "\0"

    # gets next token
    def get_token(self):
        # next token until eof
        while not self.__iseof:
            if  self.__ignore():
                continue
            # extract!!
            elif self.__stack.push(self.__idn()):
                return self.__stack.pop()
            elif self.__stack.push(self.__num()):
                return self.__stack.pop()
            elif self.__stack.push(self.__str()):
                return self.__stack.pop()
            elif self.__stack.push(self.__opt()):
                return self.__stack.pop()
            else:
                return self.__err()
        
        # empty!
        self.__stack.clear()
        # return new eof token
        return self.__eof()
    
    # sets input file
    def feed_input(self, _src_path:str, _raw_string:str):
        self.__path  = _src_path
        self.__cont  = _raw_string
        self.__clook = self.__cont[0] if len(self.__cont)  > 0 else "\0"
        self.__index = 0

    def __ignore(self):
        # checker
        def is_ign(char):
            global NULLCHR, BACKSPC, TABCHAR, NEWLINE, CARRRET, WHTESPC
            return (
                char == NULLCHR or
                char == BACKSPC or
                char == TABCHAR or
                char == NEWLINE or
                char == CARRRET or
                char == WHTESPC
            )
        
        # check if satisfied
        if  not is_ign(self.__clook):
            return False

        # forward while ignoreable!
        while not self.__iseof and is_ign(self.__clook):
            self.__next_index()
        
        # return True flag
        return True
    
    # IDENTIFIER
    def __idn(self):
        # checker
        def is_idn(char):
            return (
                (ord(char) >= 0x61 and ord(char) <= 0x7a) or
                (ord(char) >= 0x41 and ord(char) <= 0x5a) or
                (ord(char) == 0x5f)
            )
        
        # check num
        def is_num(char):
            return (ord(char) >= 0x30 and ord(char) <= 0x39)

        # check if satisfied
        if  not is_idn(self.__clook):
            return False

        # record pos
        x, y = (self.__ccolm-1), self.__cline

        # temporary holder
        _tmp = ""

        # build while potential id
        while not self.__iseof and (
            is_idn(self.__clook) or 
            (len(_tmp) > 0 and is_num(self.__clook)
        )):
            _tmp += self.__clook
            self.__next_index()
        
        # return new id token
        return BToken(
            BTokenType.IDN, _tmp, 
            (x, x+len(_tmp), y, self.__cline),
            self.__path, self.__cont
        )
    
    # number
    def __num(self):
        # checker 0
        def is_num(char):
            return (
                ord(char) >= 0x30 and ord(char) <= 0x39
            )
        # checker 1
        def is_hex(char):
            nonlocal is_num
            return (
                is_num(char) or 
                ord(char) >= 0x61 and ord(char) <= 0x66 or
                ord(char) >= 0x41 and ord(char) <= 0x46
            )
        # checker 2
        def is_oct(char):
            return (
                ord(char) >= 0x30 and ord(char) <= 0x37
            )
        # checker 3
        def is_bin(char):
            return (
                ord(char) == 0x30 and ord(char) == 0x31
            )

        # check if satisfied
        if  not is_num(self.__clook):
            return False
        
        # record pos
        x, y = (self.__ccolm-1), self.__cline

        # temporary holder
        _tmp = ""

        if  self.__clook == "0":
            # check if zero.important!
            _tmp += self.__clook
            self.__next_index()
            
        # checker | handler
        _handle = None

        if  False:
            pass
        # check if other lit
        elif self.__clook == "x" or self.__clook == "X":
            # update _handler
            _handle = is_hex
            # forward
            _tmp += self.__clook
            self.__next_index()
        elif self.__clook == "o" or self.__clook == "O":
            # update _handler
            _handle = is_oct
            # forward
            _tmp += self.__clook
            self.__next_index()
        elif self.__clook == "b" or self.__clook == "B":
            # update _handler
            _handle = is_bin
            # forward
            _tmp += self.__clook
            self.__next_index()

        if  _handle:
            # forward while number
            while not self.__iseof and _handle(self.__clook):
                _tmp += self.__clook
                self.__next_index()
            else:
                _tok = BToken(
                    BTokenType.OTH, _tmp, 
                    (x, x+len(_tmp), y, self.__cline),
                    self.__path, self.__cont
                )
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "invalid number format \""+ _tok.getSymbol() + "\"!",
                    trace__token(self.__path, self.__cont, _tok)
                )
        else:
            _handle = is_num
        
        # float flag
        is_flt = False
        # truncate flag
        is_trn = False

        while True:
            # forward while number
            while not self.__iseof and _handle(self.__clook):
                _tmp += self.__clook
                self.__next_index()
            
            if  _handle != is_num:
                break
            
            # if number
            if  self.__clook == "." and not (is_flt and is_trn):
                # update
                is_flt = True
                # forward
                _tmp += self.__clook
                self.__next_index()
                
                # error if not number
                if  not _handle(self.__clook):
                    _tok = BToken(
                        BTokenType.FLT, _tmp, 
                        (x, x+len(_tmp), y, self.__cline),
                        self.__path, self.__cont
                    )
                    return errorHandler.throw__error(
                        errorType.SYNTAX_ERROR, "invalid number format \""+ _tok.getSymbol() + "\"!",
                        trace__token(_tok)
                    )
            
            # if number
            if  self.__clook == "e" and not is_trn:
                # update
                is_flt = True
                is_trn = True
                # forward
                _tmp += self.__clook
                self.__next_index()

                # error if not number
                if  not _handle(self.__clook):
                    _tok = BToken(
                        BTokenType.FLT, _tmp, 
                        (x, x+len(_tmp), y, self.__cline),
                        self.__path, self.__cont
                    )
                    return errorHandler.throw__error(
                        errorType.SYNTAX_ERROR, "invalid number format \""+ _tok.getSymbol() + "\"!",
                        trace__token(self.__path, self.__cont, _tok)
                    )
            
            # if not number
            if  not _handle(self.__clook):
                break
        
        # mark as float if needed!
        _mutable_t = BTokenType.INT if _handle == is_num else BTokenType.OTH
        if  is_flt:
            _mutable_t = BTokenType.FLT

        # return new int | float token
        return BToken(
            _mutable_t, _tmp, 
            (x, x+len(_tmp), y, self.__cline),
            self.__path, self.__cont
        )
    
    def __str(self):
        # check!!
        if  self.__clook != "\"":
            return False

        # record pos
        x, y = (self.__ccolm-1), self.__cline

        # temporary holder
        _tmp = ""
        
        openner, closer = self.__clook, None
        self.__next_index()

        # update closer
        closer = self.__clook

        if  (openner == closer):
            self.__next_index()

        _escpe  = ({
            "0" : "\0",
            "b" : "\b",
            "t" : "\t",
            "n" : "\n",
            "r" : "\n"
        })

        _add = 0

        # forward until closed
        while not self.__iseof and (openner != closer):

            if  self.__clook == "\n":
                self.__next_index()
                break

            # if slashed
            elif self.__clook == "\\":
                self.__next_index()
                _add += 1
                _tmp += _escpe[self.__clook] if  self.__clook in _escpe.keys() else ("\\" + self.__clook)
            else:
                _tmp += self.__clook
            
            self.__next_index()
            closer = self.__clook
        
            if  (openner == closer):
                self.__next_index()

        if  not (openner == closer):
            self.__next_index()
            _tok = BToken(
                BTokenType.STR, _tmp, 
                (x, x+len(_tmp), y, self.__cline),
                self.__path, self.__cont
            )
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "string \""+ _tok.getSymbol() + "\" is not closed!",
                trace__token(self.__path, self.__cont, _tok)
            )
        
        # return new string token
        return BToken(
            BTokenType.STR, _tmp, 
            (x, 1 + (x+len(_tmp)+_add) + 1, y, self.__cline),
            self.__path, self.__cont
        )

    def __opt(self):
        # checker
        def is_opt(opt):
            global OPERATORS
            # iter
            for each_opt in OPERATORS:
                if  each_opt.startswith(opt) or each_opt == opt:
                    return True
            return False
        
        # check if satisfied
        if  not is_opt(self.__clook):
            return False
        
        # record pos
        x, y = (self.__ccolm-1), self.__cline

        # temporary holder
        _tmp = ""

        if  is_opt(self.__clook) and self.__clook in ("(", "[", "{"):
            # forward
            _tmp += self.__clook
            self.__next_index()

            # return immidiately
            return self.__STACK.push(BToken(
                BTokenType.OPT, _tmp, 
                (x, x+len(_tmp), y, self.__cline),
                self.__path, self.__cont
            ))

        # find pair
        elif is_opt(self.__clook) and self.__clook in (")", "]", "}"):
            # forward
            _tmp += self.__clook

            # pop pair!
            top = self.__STACK.pop()

            # error if null
            if  not top:
                _tok = BToken(
                    BTokenType.OPT, _tmp, 
                    (x, x+len(_tmp), y, self.__cline),
                    self.__path, self.__cont
                )
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "symbol \""+ _tok.getSymbol() + "\" was never opened!",
                    trace__token(self.__path, self.__cont, _tok)
                )
            
            _sym = top.getSymbol()

            if  (
                _sym == "(" and self.__clook == ")" or
                _sym == "[" and self.__clook == "]" or
                _sym == "{" and self.__clook == "}"
            ):
                # forward !
                self.__next_index()
               
                # return immidiately if paired!
                return BToken(
                    BTokenType.OPT, _tmp, 
                    (x, x+len(_tmp), y, self.__cline),
                    self.__path, self.__cont
                )
            else:
                _tok = BToken(
                    BTokenType.OPT, _tmp, 
                    (x, x+len(_tmp), y, self.__cline),
                    self.__path, self.__cont
                )
                return errorHandler.throw__error(
                    errorType.SYNTAX_ERROR, "symbol \""+ _tok.getSymbol() + "\" was never opened!",
                    trace__token(self.__path, self.__cont, _tok)
                )

        # forward until mot operator
        while not self.__iseof and is_opt(_tmp + self.__clook):
            _tmp += self.__clook
            self.__next_index()

        # return new operator token
        return BToken(
            BTokenType.OPT, _tmp, 
            (x, x+len(_tmp), y, self.__cline),
            self.__path, self.__cont
        )
    
    def __err(self):
        # record pos
        x, y = (self.__ccolm-1), self.__cline

        # temporary holder
        _tmp  = ""
        _tmp += self.__clook

        # token
        _tok  = BToken(
            BTokenType.OPT, _tmp, 
            (x, x+len(_tmp), y, self.__cline),
            self.__path, self.__cont
        )
        # throw error
        return errorHandler.throw__error(
            errorType.SYNTAX_ERROR, "unknown token \"" + _tok.getSymbol() + "\".",
            trace__token(self.__path, self.__cont, _tok)
        )
    
    def __eof(self):
        # determine un closed token
        if  not self.__STACK.isempty():
            _chunk = ""
            while not self.__STACK.isempty():
                _chunk += trace__token(self.__STACK.pop())
            # error
            return errorHandler.throw__error(
                errorType.SYNTAX_ERROR, "these symbol(s) was never closed!",
                trace__token(self.__path, self.__cont, _chunk)
            )

        # record pos
        x, y = (self.__ccolm-1), self.__cline
        
        # return new eof token
        return BToken(
            BTokenType.EOF, "eof", 
            (x, x+3, y, self.__cline),
            self.__path, self.__cont
        )

## END