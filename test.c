#include <stdio.h>

struct Point;
int init(struct Point *this,int x,int y);
int sum(struct Point *this);
typedef struct Point{
    int x;
    int y;
    
    
} Point;
int init(struct Point *this,int x,int y){
        this->x = 10;
        this->y = 10;}
int sum(struct Point *this){return this->x+this->y;}


int main() {
    Point p[2];init(&(p[0]),10,10);init(&(p[1]),20,20);
    printf("%d\n",sum(&(p[0])));
    printf("%d\n",sum(&(p[1])));
    return 0;
}
