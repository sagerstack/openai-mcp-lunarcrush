# Software Development Rule 1: Adopt Clean Architecture and Domain-Driven Design 

## Goal
This document covers guidelines for adopting clean architecture and domain-driven-design (DDD) to write enterprise-grade application code in python

## References
Harry Percival

Blog/Website: obeythetestinggoat.com - His famous TDD resource site
GitHub: github.com/hjwp
Book: "Test-Driven Development with Python: Obey the Testing Goat"

Bob Gregory
Joint Website: cosmicpython.com (with Harry Percival)
Joint GitHub: github.com/cosmicpython/book

GitHub: github.com/bobthemighty
Book: Architecture Patterns with Python: Published by O'Reilly, it's become one of the most comprehensive resources for applying Clean Architecture, Domain-Driven Design, and Test-Driven Development principles specifically in Python
Link to the free version of the book: https://www.cosmicpython.com/book/preface.html

The book is often referred to as "Cosmic Python" because of their website domain, and it's considered essential reading for Python developers wanting to implement enterprise-level architectural patterns while maintaining good testing practices.

## Other References and Sample codes
https://thinhdanggroup.github.io/python-code-structure/
https://github.com/shaliamekh/clean-architecture-fastapi

## Include my specific requirements into the code structure as best practices
1. Organize the domain layer such that code is organized by domain entity and related classes and value objects, domain events, services and interfaces

2. Organize the use_cases layer such that the code is organized by features, and segregation between query and command use cases

3. Common domain classes should be kept under sharedkernel

4. API source codes should also include latest swagger support