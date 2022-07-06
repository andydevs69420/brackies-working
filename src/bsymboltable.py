from enum import Enum
from blogger import log__info
from berrhandler import errorHandler, errorType


class Node:pass
class Node:
    def __init__(self, _head:Node):
        self.head    = _head
        self.symbols = []
    
    def insert(self, **_prop:dict):
        _prop["index"] = len(self.symbols)
        self.symbols.append(_prop)
        return (len(self.symbols) - 1)
    
    def update(self, _symbol:str, **_new_prop):
        self.lookup(_symbol).update(_new_prop)
    
    def delete(self, _symbol:str):
        if  not self.existL(_symbol):return False
        for idx in range(len(self.symbols)):
            if  self.symbols[idx]["symbol"] == _symbol:
                del self.symbols[idx]
                return True
        return False 
    
    def existL(self, _symbol:str):
        for each_symbol in self.symbols:
            if each_symbol["symbol"] == _symbol:
                return True
        return False
    
    def lookup(self, _symbol:str):
        node = self
        while node.head != None:
            for each_symbol in node.symbols:
                if each_symbol["symbol"] == _symbol:
                    return each_symbol
            node = node.head
        for each_symbol in node.symbols:
            if each_symbol["symbol"] == _symbol:
                return each_symbol
        return False
    
    def print_table(self):
        node = self
        while node.head != None:
            log__info(node.symbols.__str__())
            node = node.head
        log__info(node.symbols.__str__())
        

class SymbolType(Enum):
    TEMPORARY = 0x01
    PERMANENT = 0x02 

class SymbolTable:

    CURR = None
    PREV = []
        
    @staticmethod
    def new_scope():
        if SymbolTable.CURR != None:SymbolTable.PREV.append(SymbolTable.CURR)
        SymbolTable.CURR = Node(SymbolTable.CURR) # new node
    
    @staticmethod
    def insert(**_prop:dict):
        return SymbolTable.CURR.insert(**_prop)

    @staticmethod
    def update(_symbol:str, **_prop:dict):
        return SymbolTable.CURR.update(_symbol, **_prop)

    @staticmethod
    def delete(_symbol:str, **_prop:dict):
        return SymbolTable.CURR.delete(_symbol)
    
    @staticmethod
    def existL(_symbol:str):
        return SymbolTable.CURR.existL(_symbol)

    @staticmethod
    def lookup(_symbol:str):
        return SymbolTable.CURR.lookup(_symbol)

    @staticmethod
    def end_scope():
        if len(SymbolTable.PREV) > 0:SymbolTable.CURR = SymbolTable.PREV.pop()

    @staticmethod
    def get_cnode():
        return SymbolTable.CURR