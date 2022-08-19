# brackies-working
Brackies programming language
# DESCRIPTION
A not so trash programming language written in python,
uses LL recursive descent to parse the input.

# HOW TO RUN
### windows: <br/>
&nbsp;&nbsp;&nbsp;&nbsp;py src/brackies.py -f path/to/file.bruh
### linux/mac: <br/>
&nbsp;&nbsp;&nbsp;&nbsp;python3 src/brackies.py -f path/to/file.bruh

# BASIG USAGE
```javascript

    /** basic datatype **/
    /*
        Int  -> integer 
        Flt  -> float
        Str  -> string
        Bool -> boolean
        Null -> nulltype // null is also a type here!
        List -> list
        Func -> function
        Type -> type
        BoundMethod -> default object method(s)
        BuildinFunc -> builtin functions such as (write, println, scan, readFile)
        BrackiesCode -> ByteCode(as string)

        NOTE:
            you can use "Any" if you are not sure to its runtime type..
            example: 
                var x:Any = "string".toString;
                println(x.typeString());
                // produces: "BoundMethod"
    */

    /** defining a global variable **/
    // syntax:= "var" name : type = value, *;
    var x:Int = 200, y:Flt = 2.0;

    // converts number to string
    var x_as_str:Str = x.toString();
    var x_as_type_str:Str = x.typeString();
    var x_as_type:Type = x.type();


    /************* string *************/

    // string comparison
    var result:Bool = "hello".equals("world");

    // string length
    println("Hello".length());
    // produces: 5

    // string concatenation
    println("Hello ".concat("World!"));
    // produces: "Hello World!" or if the argument passed is not a string, it returns null.


    /************* list *************/
    var lst:List[Int] = [1, 2, 3];

    println(lst.typeString());
    // produces: "List_of_Int"

    /** list operation **/

    // removes and returns the last element of the list
    println(lst.pop());
    // produces: 3

    // pushes element into list
    println(lst.push(obj));

    // counts the element inside the list
    println(lst.length());
    // produces: 2


    /************* defining a function *************/
    
    function fact:Int(_n:Int) {

        if (_n <= 1) return 1;

        return _n * fact(_n - 1);
    }

# STATUS
- Discontinued!!! I'dont remember a single thing about what I've written. F!!!!

