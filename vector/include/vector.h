#ifndef VECTOR_H
#define VECTOR_H

#include "point.h"
#include <cmath>

class Vector : public Point {
public:
    Vector(double x = 0.0, double y = 0.0);
    Vector(const Point& p);

    double magnitude() const;

    Vector operator*(double scalar) const;
    double operator*(const Vector& other) const;
    double operator/(const Vector& other) const;
    Vector operator+(const Vector& other) const;
    Vector operator-(const Vector& other) const;
    bool operator==(const Vector& other) const;

    friend std::ostream& operator<<(std::ostream& os, const Vector& v);
    friend std::istream& operator>>(std::istream& is, Vector& v);
};

bool arePerpendicular(const Vector& v1, const Vector& v2);
double angleBetween(const Vector& v1, const Vector& v2);

#endif 