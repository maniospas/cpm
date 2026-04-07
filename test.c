#include <stdio.h>

// support for self. as equivalent to this->
struct Point;
int init(struct Point *this, int x, int y);
int sum(struct Point *this);
typedef struct Point{
    int x;
    int y;
    
    
}Point;
int init(struct Point *this, int x, int y){
        this->x = 10;
        this->y = 10;}
int sum(struct Point *this){return this->x+this->y;}



int main() {
    Point p = .init(10,10);
    printf("%d\n", p.sum());
    return 0;
}
