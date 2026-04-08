#include<stdint.h>
typedef int8_t  i8;
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;
typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef float f32;
typedef double f64;
#define delete(ptr) if(ptr)free(ptr);ptr=0;
#include <stdio.h>
#include <stdlib.h>


struct Point;
struct Point* init(struct Point *this,i64 x,i64 y);
i64 sum(struct Point *this);
typedef struct Point{
    i64 x;
    i64 y;
    
    
} Point;
struct Point* init(struct Point *this,i64 x,i64 y){(*this).x = x; (*this).y = y;return this;}
i64 sum(struct Point *this){return (*this).x+(*this).y;}

int main() {
    Point* p =init(malloc(sizeof*p),10,10);
    printf("%ld\n",sum(p));
    return 0;
}
