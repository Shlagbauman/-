#ifndef POINT_H
#define POINT_H

#include <iostream>

class Point {
private:
    double x;
    double y;
public:
    Point(double x = 0.0, double y = 0.0);

    double getX() const;
    double getY() const;
    void setX(double x);
    void setY(double y);

    friend std::ostream& operator<<(std::ostream& os, const Point& p);
    friend std::istream& operator>>(std::istream& is, Point& p);
};

#endif 
