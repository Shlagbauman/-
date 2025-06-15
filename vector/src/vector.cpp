#include "../include/vector.h"

Vector::Vector(double x, double y) : Point(x, y) {}
Vector::Vector(const Point& p) : Point(p) {}

double Vector::magnitude() const {
    return std::sqrt(getX() * getX() + getY() * getY());
}

Vector Vector::operator*(double scalar) const {
    return Vector(getX() * scalar, getY() * scalar);
}

double Vector::operator*(const Vector& other) const {
    return getX() * other.getX() + getY() * other.getY();
}

double Vector::operator/(const Vector& other) const {
    return getX() * other.getY() - getY() * other.getX();
}

Vector Vector::operator+(const Vector& other) const {
    return Vector(getX() + other.getX(), getY() + other.getY());
}

Vector Vector::operator-(const Vector& other) const {
    return Vector(getX() - other.getX(), getY() - other.getY());
}

bool Vector::operator==(const Vector& other) const {
    return getX() == other.getX() && getY() == other.getY();
}

std::ostream& operator<<(std::ostream& os, const Vector& v) {
    os << "[" << v.getX() << ", " << v.getY() << "]";
    os << " (len=" << v.magnitude() << ")";
    return os;
}

std::istream& operator>>(std::istream& is, Vector& v) {
    double x, y;
    is >> x >> y;
    v.setX(x);
    v.setY(y);
    return is;
}

bool arePerpendicular(const Vector& v1, const Vector& v2) {
    return (v1 * v2) == 0;
}

double angleBetween(const Vector& v1, const Vector& v2) {
    double dot = v1 * v2;
    double mag1 = v1.magnitude();
    double mag2 = v2.magnitude();
    return std::acos(dot / (mag1 * mag2)) * 180.0 / 3.14159265358979323846;
}