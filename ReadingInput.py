#!/usr/bin/env python
# -*- coding: utf-8 -*-


f = open("input.txt", "r")

stringSalida = ''

while True:
    line = f.readline()
    if not line:
        break
    else:
        # Remove end lines
        posEndline = line.find('\n')
        if posEndline != -1:
            line = line[0:posEndline]
        
        #remove tabs
        posTab = line.find('\t')
        while posTab != -1:
            longLine = len(line)
            line = line[posTab+1:longLine]
            posTab = line.find('\t')
        
        # Concatenate fitered line
        stringSalida += line + ' '



print(stringSalida)