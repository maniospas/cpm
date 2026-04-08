# C± (Cpm)

*It's more or less C. With some niceties.*

A small prototype that injects lightweight class organization of C structs.
Valid programs are all C programs, with the fhe addition of some zero-cost abstractions around structs.


## 🚀 Quickstart

Consider this example program:

```c
// test.cpm
#include <stdio.h>

// classes are basically structs
// pub functions are monomorphic AND (currently) can be implemented for one class only
// support for `self.` as equivalent to `this->`
class Point {
    int x;
    int y;
    pub init(int x, int y) { // absense of return type returns `this`
        self.x = x;
        self.y = y;
    }
    pub int sum() {return this->x+this->y;}
};

int main() {
    Point p.init(10,10);
    printf("%d\n", p.sum());
    return 0;
}
```

Convert the program to C and run it:

```bash
python3 -m cpm test.cpm
>>> test.cpm converted to test.c
gcc test.c -o test -O2
./test
>>> 20
```


## 📋 Extra syntax

**classes**

- `class Name {...};` is equivalent to `typedef struct Name {...} Name;`
- `pub rettype name(args)` declares methods **inside classes**
- `obj.method(args)` or `objptr->method(args)` call mehods, where the first case uses the object's reference

Methods of the same struct use forward declarations to see each other and the struct.
They also count as publicly accessible functions, with the
difference that there is a hidden pointer to the struct on the variable `this`.
Use _self_ instead of _*this_ for more comprehensive code.

Methods that do not declare any return type are made to return `this`.
This means that the following syntax is valid:

```c
class Point {
    i64 x;
    i64 y;
    pub init(i64 x, i64 y) {
        if(!this) return this; // elegant handling of NULL
        self.x = x;
        self.y = y;
    }
    pub i64 sum() {return self.x+self.y;}
};
...

Point* p = malloc(sizeof*p)->init(10,10);
```

For the same class, C± also allows in-place initialization with the following pattern.

```c
Point p.init(10,10); // equivalent to Point p;p.init(10,10);
```

**ergonomic types**

C± typedefs fixed-width arithmetic types, namely i8-i64, u8-u64, f32, and f64.
Prefer using these, as they are generally easier to work with. Furthermore,
`const char*` is typdef-ed as `cstr`.

An important feature is that all identical `cstr` in your program are forced to have the same memory address,
so that you can write code like the following; most compilers support literal merging -and have it be turned
on by default- but that is technically undefined behavior in the C specs. Not in C±.

```c
#include <stdio.h>

int main() {
    cstr x = "A";
    cstr y = "A";
    if(x==y) printf("A!\n");
    return 0;
}
```

**delete**

C± defines a `delete` macro that performs a `free` after a NULL check and then sets to NULL.
This means, that you can try to delete the same pointers multiple times. Here is an example.

```c
Point* create_p() {
   Point* p1 = malloc(sizeof*p1)->init(10,10);
   Point* p2 = malloc(sizeof*p2)->init(10,10);
   Point* p3 = malloc(sizeof*p3)->init(10,10);
   if(!(p1&&p2&&p3)) goto done:

   done:
   delete(p2);
   delete(p3);
   return p1;
}
```


