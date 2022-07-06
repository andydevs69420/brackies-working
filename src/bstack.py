
__ALL__ = [ "BStack" ]

# Brackies stack implementation
from blogger import log__error, log__info
from berrhandler import errorHandler, errorType


class BStack(object):
    def __init__(self):
        self.__stack_internal = []

    def pop(self):
        # empty check!
        if  self.isempty():
            return None
        # returns popped item
        return self.__stack_internal.pop()

    def push(self, _any:object):
        # append internally
        self.__stack_internal.append(_any)
        # return top item
        return _any
    
    def isempty(self):
        return len(self.__stack_internal) <= 0
    
    def clear(self):
        for itm in self.__stack_internal:
            del self.__stack_internal[itm]
    
    def dump(self):
        if self.isempty():
            return log__info("empty!")

        for each in self.__stack_internal:
            log__info(each.__str__())
        
        errorHandler.throw__error(
            errorType.UNEXPECTED_ERROR, "fatal!!!! dumped."
        )
