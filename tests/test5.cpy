#$ ELEFTHERIOS MARIOS MANIKAS AM:4723 #$
#$ STEFANOS FOTOPOULOS AM:4829 #$
def main_fibonacci():
#{
    #declare x
    def fibonacci(x):
    #{
        if (x<=1):
            return(x);
        else:
            return (fibonacci(x-1)+fibonacci(x-2));
    #}
    x = int(input());
    print(fibonacci(x));
#}