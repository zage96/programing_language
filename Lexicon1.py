#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ply.lex as lex
import codecs
import os
import re
import sys


# create the reserved words
reserved ={
    'PROGRAM':'PROGRAM',
    'END':'END',
    'DIM':'DIM',
    'of':'of',
    'double':'double',
    'word':'word',
    'matrix':'matrix',
    'size':'size',
    'SUB':'SUB',
    'PROCEDURE':'PROCEDURE',
    'RETURN':'RETURN',
    'BEGIN':'BEGIN',
    'IF':'IF',
    'THEN':'THEN',
    'ELSE':'ELSE',
    'ENDIF':'ENDIF',
    'INPUT':'INPUT',
    'WHILE':'WHILE',
    'WEND':'WEND',
    'DO':'DO',
    'LOOP':'LOOP',
    'FOR':'FOR',
    'NEXT':'NEXT',
    'GOSUB':'GOSUB',
    'LET':'LET',
    'OUTPUT':'OUTPUT',
    'AND' : 'AND',
    'OR': 'OR',
    'NOT' : 'NOT'
}


# Create the tokens
tokens = [
    'id',
    'DosPuntos',
    'PuntoYComa',
    'Coma',
    'CorcheteA',
    'CorcheteC',
    'numero',
    'DosPuntosIgual',
    'ParentesisA',
    'ParentesisC',
    'Gato',
    'Comillas',
    'Mayor',
    'Menor',
    'MayorIgual',
    'MenorIgual',
    'Igual',
    'Diferente',
    'Mas',
    'Menos',
    'Por',
    'Entre',
    'Potencia',
    'GuionBajo',
    'SignoInterr'
]


# Group all the tokens and reserved words in one
tokens = tokens + list(reserved.values())

#Tokens simples
t_Igual= r'\='
t_DosPuntos= r'\:'
t_DosPuntosIgual= r'\:='
t_Mayor= r'\>'
t_Menor= r'\<'
t_PuntoYComa= r'\;'
t_Coma= r'\,'
t_CorcheteA= r'\['
t_CorcheteC= r'\]'
t_ParentesisA= r'\('
t_ParentesisC= r'\)'
t_Gato= r'\#'
t_Comillas= r'\"'
t_MayorIgual= r'\>='
t_MenorIgual= r'\<='
t_Diferente= r'\<>'
t_Mas= r'\+'
t_Menos= r'\-'
t_Por= r'\*'
t_Entre= r'\/'
t_Potencia= r'\^'
t_GuionBajo = r'\_'
t_SignoInterr = r'\?'


def t_id(t):
    r'[a-zA-Z][_a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'id') # Check for reserved words
    return t

def t_numero(t):
    r'[\-]?[0-9]+(\.[0-9]+)?'
    thisNumber = t.value
    findPunto = thisNumber.find('.')
    if findPunto != -1 :
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


# New line detection
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Build the lexer
lexer = lex.lex()

#######################
'''data = '-3.0'
lexer.input(data)


while True:
    tok = lexer.token()
    if not tok: 
        break     
    print(tok)
'''