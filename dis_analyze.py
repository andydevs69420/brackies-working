import dis

code = """
class Dog:

    x = 2

    def eat(x):
        print(x)
    def bark(x):
        print(x)

hola = 2
"""

dis.dis(code)





