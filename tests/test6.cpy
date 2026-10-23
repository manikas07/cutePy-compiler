#$ nested functions, non-local variables, and/or/not #$
def main_nested():
#{
    #declare a, b
    def outer2(q):
    #{
        return (q * (-2));
    #}
    def outer(x):
    #{
        #declare y
        def inner(z):
        #{
            a = a + z;
            return (x + y + z + a);
        #}
        def twice(w):
        #{
            return (inner(w) + inner(w));
        #}
        y = 100;
        return (twice(x) + outer2(x));
    #}
    a = 1;
    b = outer(3);
    print(a);
    print(b);
    print(-7 // 2);
    if (a > 1 and b > 1 or not [a == b]):
        print(1);
    else:
        print(0);
    while ([a < 20] and a != 12):
        a = a + 1;
    print(a);
#}
def main_second():
#{
    #declare a
    a = 5;
    print(a);
#}
if __name__ == "__main__":
    main_second();
    main_nested();
    main_second();
