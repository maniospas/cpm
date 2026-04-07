# c± (cpm)

A small prototype that injects lightweight class organization of C structs.
PATTERN MATCHING IS NOT 100% CORRECT AND MAY AFFECT STRINGS INTERIORS.
Example program:

```c
// test.cpm
#include <stdio.h>

// classes are basically structs
// pub functions are monomorphic AND (currently) can be implemented for one class only
// support for self. as equivalent to this->
class Point {
    int x;
    int y;
    pub void init(int x, int y) {
        self.x = x;
        self.y = y;
    }
    pub int sum() {return this->x+this->y;}
};

int main() {
    Point p;
    p.init(10,10);
    printf("%d\n", p.sum());
    return 0;
}
```

Convert the program to C and run it:

```bash
python3 -m cpm test.cpm
>>> test.cpm >> test.c
gcc test.c -o test -O2
./test
>>> 20
```



