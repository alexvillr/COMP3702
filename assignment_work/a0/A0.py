# -*- coding: utf-8 -*-
"""
Assignment 0 template

For submission, rename this file to "A0.py" 

Answer each question in the corresponding method definition stub below
"""


def Q1(A,B):
    union = set()
    intersection = set()
    if (len(A) > len(B)):
        union = A
        for element in B:
            if not element in union:
                union.add(element)
            
            if element in A:
                intersection.add(element)
        
    else:
        union = B
        for element in A:
            if not element in union:
                union.add(element)
            
            if element in B:
                intersection.add(element)

    return union,intersection


def Q2(A,B):
    for element in A:
        if element in B:
            return 'INTERSECTING'
    for element in B:
        if element in A:
            return 'INTERSECTING'
    return 'DISJOINT'


def Q3(a,b):
    X = set()
    Y = set()
    G = set()
    return X,Y,G


def Q4(E,n):
    n_successors = []
    return n_successors


def Q5(inFile,outFile,remove):
    print('Character '+remove+' removed from '+inFile)
    print('Output written to '+outFile)


def Q6(state1,state2):
    print('IMPOSSIBLE')