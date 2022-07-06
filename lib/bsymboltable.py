from enum import Enum
from berrhandler import errorHandler, errorType
class BSymbolTable:

    TABLE_STACK  = []
    CURRENT      = None

    HISTORY      = []

    @staticmethod
    def dump_when_empty():
        # check
        if  len(BSymbolTable.HISTORY) <= 0 and BSymbolTable.CURRENT == None:
            # throws error
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "fatal!!!! empty scope."
            )

    @staticmethod
    def new_scope():
        # record current
        BSymbolTable.HISTORY.append(len(BSymbolTable.TABLE_STACK))

        # check if none | global
        if  BSymbolTable.CURRENT == None: # []
            BSymbolTable.CURRENT = ({
                "parent"  : 0,
                "self"    : 0,
                "symbols" : []
            })
            return 0
        
        # index
        _index = len(BSymbolTable.TABLE_STACK)
        
        # append
        BSymbolTable.TABLE_STACK.append(BSymbolTable.CURRENT)

        # new
        BSymbolTable.CURRENT = ({
            "parent"  : _index,
            "self"    : (_index + 1),
            "symbols" : []
        })

        return (_index + 1)
    
    @staticmethod
    def end_scope():
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        # pop from history
        _current = BSymbolTable.HISTORY.pop()
        if  _current <= 0 and len(BSymbolTable.TABLE_STACK) <= 0:
            return
        
        BSymbolTable.TABLE_STACK.append(BSymbolTable.CURRENT)
        
        # back to prev
        BSymbolTable.CURRENT = BSymbolTable.TABLE_STACK[_current]
    
    @staticmethod
    def change_scope(_scope_index:int):
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        if  len(BSymbolTable.TABLE_STACK) <= 0:
            return
    
        BSymbolTable.CURRENT = BSymbolTable.TABLE_STACK[_scope_index]

    @staticmethod
    def get_local_index():
        return len(BSymbolTable.CURRENT["symbols"])

    @staticmethod
    def new_symbol(prop:dict):
        # required property!
        _required = [
            ("symbol" , str),
        ]

        # throws error when empty!
        BSymbolTable.dump_when_empty()

        for each_req in _required:
            if  each_req[0] not in prop.keys():
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! required prop does not exist \"" + each_req[0] + "\"!"
                )
            elif each_req[1] != type(prop[each_req[0]]):
                # throws error
                return errorHandler.throw__error(
                    errorType.UNEXPECTED_ERROR, "fatal!!!! prop \"" + each_req[0] + "\" type mismatch ("+ each_req[0] +") \"" + each_req[1].__name__ + "\" != \"" + type(prop[each_req[0]]).__name__ + "\"."
                )

        (BSymbolTable.CURRENT["symbols"]
        .append(prop))

        return BSymbolTable.get_local_index() - 1
    
    @staticmethod
    def update_symbol(_symbol:str, **_new_prop):
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        point = BSymbolTable.retrieve_symbol_address(_symbol)
        if  len(BSymbolTable.TABLE_STACK) <= 0:
            print("HERE 0")
            for k, v in zip(_new_prop.keys(), _new_prop.values()):
                if  k in BSymbolTable.CURRENT["symbols"][point[1]].keys():
                    BSymbolTable.CURRENT["symbols"][point[1]][k] = v
                else:
                    # throws error
                    return errorHandler.throw__error(
                        errorType.UNEXPECTED_ERROR, "!!!! invalid prop \"" + k + "\"!"
                    )
        else:
            for k, v in zip(_new_prop.keys(), _new_prop.values()):
                if  k in BSymbolTable.TABLE_STACK[point[0]]["symbols"][point[1]].keys():
                    BSymbolTable.TABLE_STACK[point[0]]["symbols"][point[1]][k] = v

                else:
                    # throws error
                    return errorHandler.throw__error(
                        errorType.UNEXPECTED_ERROR, "!!!! invalid prop \"" + k + "\"!"
                    )

    @staticmethod
    def exist_in_scope(_symbol:str):
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        # iter
        for each_sym in BSymbolTable.CURRENT["symbols"]:
            if  each_sym != None:
                if  each_sym["symbol"] == _symbol:
                    return True

        # not exist
        return False

    
    @staticmethod
    def exist_in_parent_scope(_symbol:str):
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        _current = BSymbolTable.CURRENT

        if  _current["parent"] == 0:
            return BSymbolTable.exist_in_scope(_symbol)


        _parent = BSymbolTable.TABLE_STACK[_current["parent"]]
        while _parent["parent"] != 0:

            # iter
            for each_sym in _parent["symbols"]:
                if  each_sym != None:
                    if  each_sym["symbol"] == _symbol:
                        return True

            _parent = BSymbolTable.TABLE_STACK[_parent["parent"]]
        
        # not exist
        return False
    
    
    @staticmethod
    def retrieve(_symbol:str):
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        # check ixistence
        if  not BSymbolTable.exist_in_parent_scope(_symbol):
            # throws error
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "fatal!!!! not existent symbol \"" + _symbol + "\"."
            )

        _current = BSymbolTable.CURRENT

      

        _parent = _current
        
        while _parent["parent"] >= 0:

            # iter
            for each_sym in _parent["symbols"]:
                if  each_sym != None:
                    if  each_sym["symbol"] == _symbol:
                        return each_sym

            _parent = BSymbolTable.TABLE_STACK[_parent["parent"]]

    @staticmethod
    def retrieve_symbol_address(_symbol:str):
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        # check ixistence
        if  not BSymbolTable.exist_in_parent_scope(_symbol):
            # throws error
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "fatal!!!! not existent symbol \"" + _symbol + "\"."
            )

        _current = BSymbolTable.CURRENT
        _parent = _current
        
        while _parent["parent"] >= 0:

            _idx0 = 0
            # iter
            for each_sym in _parent["symbols"]:
                if  each_sym != None:
                    if  each_sym["symbol"] == _symbol:
                        return (_parent["self"], _idx0)
                _idx0 += 1

            _parent = BSymbolTable.TABLE_STACK[_parent["parent"]]
    

    @staticmethod 
    def retrive_at(_address:tuple[int,int]):
        # throws error when empty!
        BSymbolTable.dump_when_empty()

        if  type(_address) != tuple:
            # throws error
            return errorHandler.throw__error(
                errorType.UNEXPECTED_ERROR, "invalid type \"" + type(_address).__name__ + "\" != " + "\"tuple\""
            )
        
        if  len(BSymbolTable.TABLE_STACK) <= 0 :
            return BSymbolTable.CURRENT["symbols"][_address[1]]
        else:
            return BSymbolTable.TABLE_STACK[_address[0]]["symbols"][_address[1]]




