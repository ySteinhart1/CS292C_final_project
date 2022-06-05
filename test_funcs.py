def simple_test(x):
    return x[0]

def simple_test_2(x):
    a = 4
    return x + a

def multi_param_2(x, y):
    a = 4
    b = "s"
    
    c = x + a
    d = y + b
    return x + y

def simple_multi_param(x, y):
    return x + y

def simple_bool(x, y, z):
    a = 1
    if x:
        y += a
    else:
        z += a
    return not x

def simple_attr(x, y):
    if x.isdigit():
        y = 2
    return y

def test_mult(x):
    a = x[0]
    return x * 2

def simple_return(x):
    return x

def test_subtract(x, y):
    return x - y

def test_complex(a, b, c):
    x = int(a)
    if (a.isupper()):
        b += x
        c += 1
    return b + c

def test_compare(a, b):
    return a < b

def test_bool(a, b):
    return a and b