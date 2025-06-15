#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include "../include/vector.h"

int main() {
    std::vector<Vector> vectors;
    std::mt19937 gen(69); 
    std::uniform_real_distribution<> dis(-14.0, 14.0);

    for (int i = 0; i < 15; ++i) {
        vectors.emplace_back(dis(gen), dis(gen));
    }

    std::sort(vectors.begin(), vectors.end(),
        [](const Vector& a, const Vector& b) {
            return a.magnitude() < b.magnitude();
        });

    std::cout << "Vectors:\n";
    for (const auto& v : vectors) {
        std::cout << v << '\n';
    }

    Vector v1(1, 9), v2(9, 3);
    std::cout << "\nActions:\n"
        << "v1: " << v1 << "\nv2: " << v2 << "\n"
        << "v1 * 5: " << v1 * 5 << "\n"
        << "v1 * v2 : " << v1 * v2 << "\n"
        << "v1 / v2 : " << v1 / v2 << "\n"
        << "v1 + v2: " << v1 + v2 << "\n"
        << "v1 - v2: " << v1 - v2 << "\n"
        << "Perpendicular (1 = TRUE, 0 = FALSE) " << arePerpendicular(v1, v2) << "\n"
        << "Corner: " << angleBetween(v1, v2) << "°\n";

    return 0;
}