from sys import stdout, stderr, exit

__ALL__ = [ "log__error" ]


def log__info(_msg:str):
    # write error to stderr and exit
    stdout.write(_msg + "\n")

def log__error(_msg:str):
    # write error to stderr and exit
    stderr.write("\033[31m" + _msg + "\033[0m" + "\n")
    # exit code 1
    exit(0x01)