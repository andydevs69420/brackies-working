from core.bobject import *
from sys import stdin

def typeCheck(_opt:str, _lhs:any, _rhs:any):
        # supported type
        _support = tuple([
            (("*" , "/" , "%", "+", "-"), tuple([Int, Flt])       ),
            (("<<", ">>",              ), tuple([Int])            ),
            (("<" , "<=", ">", ">="    ), tuple([Int, Flt])       ),
            (("&" , "^" , "|"          ), tuple([Int])            ),
            (("==", "!="               ), tuple([Int, Flt, Bool] )),
            (("&&", "||"               ), tuple([Bool])           ),
        ])
        # iter!!
        for each_type in _support:
            if  _opt in each_type[0]:
                if  type(_lhs) in each_type[1] and type(_rhs) in each_type[1]:
                    return True
        # type error
        return False

def evaluate(_opt:str, _lhs:int or float, _rhs:int or float):
    _type = None
    # # determine type
    # if   type(_lhs) == int and type(_rhs):
    #     _type = Int
    # elif type(_lhs) in (int, float) or type(_rhs) in (int, float):
    #     _type = Flt
    # elif type(_lhs) == bool and type(_rhs) == bool:
    #     _type =  Bool
    
    #############################################
    _new_type = tuple([
        (("*" , "/" , "%", "+", "-" ), [((int , int  ), Int ), ((int, float), Flt)  ]),
        (("<<", ">>"                ), [((int , int  ), Int )                       ]),
        (("<" , "<=", ">", ">="     ), [((int , float), Bool)                       ]),
        (("&" , "^" , "|"           ), [((int , int  ), Int )                       ]),
        (("==", "!="                ), [((int , int, bool), Bool)                   ]),
        (("&&", "||"                ), [((bool,          ), Bool)                   ]),
    ])

    for each_type in _new_type:

        if  _opt in each_type[0]:
            for each_return_type in each_type[1]:
                if type(_lhs) in each_return_type[0] and type(_rhs) in each_return_type[0]:
                    _type = each_return_type[1]
                    break
        if  _type:
            break

    ####################### eval op #######################
    if  not _type:
        pass
    elif _opt == "*":
        return _type(_lhs *  _rhs)
    elif _opt == "/":
        _res = _lhs / _rhs
        if  type(_lhs) == int and type(_rhs) == int:
            _res = int(_res)
        return _type(    _res     )
    elif _opt == "%":
        return _type(_lhs %  _rhs )
    elif _opt == "+":
        return _type(_lhs +  _rhs )
    elif _opt == "-":
        return _type(_lhs -  _rhs )
    elif _opt == "<<":
        return _type(_lhs << _rhs )
    elif _opt == ">>":
        return _type(_lhs >> _rhs )
    elif _opt == "<":
        return _type(_lhs <  _rhs )
    elif _opt == "<=":
        return _type(_lhs <= _rhs )
    elif _opt == ">":
        return _type(_lhs >  _rhs )
    elif _opt == ">=":
        return _type(_lhs >= _rhs )
    elif _opt == "&":
        return _type(_lhs &  _rhs )
    elif _opt == "^":
        return _type(_lhs ^ _rhs  )
    elif _opt == "|":
        return _type(_lhs | _rhs  )
    elif _opt == "==":
        return _type(_lhs == _rhs )
    elif _opt == "!=":
        return _type(_lhs != _rhs )
    elif _opt == "&&":
        return _type(_lhs and _rhs)
    elif _opt == "||":
        return _type(_lhs or _rhs )



def scan(_object:FunctionParameter):
    return Str(input(_object.pop().toString().pyData()))

def write(_object:FunctionParameter):
    print(_object.pop().toString().pyData(), end="")
    return Null(None)

def println(_object:FunctionParameter):
    print(_object.pop().toString().pyData())
    return Null(None)

def readFile(_object:FunctionParameter):
    _path = _object.pop().toString().pyData()
    try:
        return Str(open(_path, "r").read())
    except FileNotFoundError:
        return Null(None)