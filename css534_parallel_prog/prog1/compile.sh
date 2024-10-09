#!/bin/sh

g++ initialize.cpp -o initialize
g++ -c EvalXOverMutate_template.cpp -fopenmp
g++ -c Timer.cpp
g++ -pg Tsp.cpp Timer.o EvalXOverMutate_template.o -fopenmp -o Tsp



