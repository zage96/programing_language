#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ply.yacc as yacc
import re
from Lexico import tokens
import sys
from tabFolder.tabulate import tabulate


# Global variables
tablaVariables = []
tablaValores = []
tablaTipo = []
posVar = 0
posTipo = 0
PilaOperandos = []
AvailTemp = ['$t1', '$t2', '$t3', '$t4', '$t5','$t6', '$t7', '$t8', '$t9', '$t10']
ValoresTemporales = ['U','U','U','U','U','U','U','U','U','U']
Cuadruplos = []
cont = 0
PilaSaltos = []
tablaMatrices = []
tablaMatricesValores = []
operandoMatriz = False
DosDimensiones = False
tablaSubRutinas = []
tablaSubRutinasDirecciones = []
PilaOperacion = []
stringOutput = ''

def creaCuadruplo(operando):
    global PilaOperandos
    global AvailTemp
    global Cuadruplos
    global cont
    global PilaSaltos
    
    if (operando == ':='):
        print("cuadruplo :=")
        # Obtener los operandos de la pila
        OP1 = PilaOperandos.pop()
        OP2 = PilaOperandos.pop()
        
        # Crear cuadruplo
        Cuad = (operando,OP1,'', OP2)
        Cuadruplos.append(Cuad)
        cont += 1

        # regresar los temporales en caso de haberse usado
        if isinstance(OP2, str):
            if OP2[0] == '$':
                AvailTemp.append(OP2)
        if isinstance(OP1, str):
            if OP1[0] == '$':
                AvailTemp.append(OP1)

    elif (operando == 'goto'):
        print("cuadruplo goto")
        Cuad = (operando,'_','','')
        Cuadruplos.append(Cuad)
        cont += 1
        
    elif (operando == 'gotoF'):
        print("cuadruplo gotoF")
        # Obtener los operandos de la pila
        OP1 = PilaOperandos.pop()

        # Se crea cuadruplo
        Cuad = (operando,OP1,'_','')
        Cuadruplos.append(Cuad)
        cont += 1
        
        # regresar los temporales en caso de haberse usado
        if isinstance(OP1, str):
            if OP1[0] == '$':
                AvailTemp.append(OP1)

    elif (operando == 'gotoV'):
        print("cuadruplo gotoV")

        # Obtener los operandos de la pila
        OP1 = PilaOperandos.pop()

        # Crear cuadruplo
        Cuad = (operando,OP1,'_','')
        Cuadruplos.append(Cuad)
        cont += 1

        # regresar los temporales en caso de haberse usado
        if isinstance(OP1, str):
            if OP1[0] == '$':
                AvailTemp.append(OP1)

    elif (operando == 'return'):
        print("cuadruplo return")
        Cuad = (operando,'','','')
        Cuadruplos.append(Cuad)
        cont += 1

    elif (operando == 'gosub'):
        print("cuadruplo gosub")
        Cuad = (operando,'_','','')
        Cuadruplos.append(Cuad)
        cont += 1

    elif (operando == 'input'):
        print('cuadruplo input')
        Cuad = (operando,'_','','')
        Cuadruplos.append(Cuad)
        cont += 1

    elif (operando == 'outputS'):
        print('cuadruplo outputS')
        Cuad = (operando,stringOutput,'','')
        Cuadruplos.append(Cuad)
        cont += 1

    elif (operando == 'outputV'):
        print('cuadruplo outputV')
        operandoImprimir = PilaOperandos.pop()
        Cuad = (operando,operandoImprimir,'','')
        Cuadruplos.append(Cuad)
        cont += 1

    else :
        print("cuadruplo logico")
        # Obtener los operandos de la pila
        OP2 = ''
        OP1 = ''
        
        while (OP2 == '' or OP2=='(' or OP2==')'):
            OP2 = PilaOperandos.pop()
        while (OP1 == '' or OP1=='(' or OP1==')'):
            OP1 = PilaOperandos.pop()
        
        #obtener un temporal
        Temporal = AvailTemp.pop()
        
        # Crear cuadruplo
        Cuad = (operando,OP1,OP2, Temporal)
        Cuadruplos.append(Cuad)
        cont += 1
        
        # agregar el temporal a pila de operandos
        PilaOperandos.append(Temporal)

        # regresar los temporales en caso de haberse usado
        if isinstance(OP2, str):
            if OP2[0] == '$':
                AvailTemp.append(OP2)
        if isinstance(OP1, str):
            if OP1[0] == '$':
                AvailTemp.append(OP1)

def Rellena(indice,direccionSalto):
    global Cuadruplos

    #Se obtiene cuadruplo
    Cuad = Cuadruplos[indice]

    #se obtiene su tipo de goto
    tipoGoto = Cuad[0]

    if(tipoGoto == 'goto' or tipoGoto == 'gosub' or tipoGoto == 'input'):
       #Se crea nuevo cuadruplo (nose permite modificar tuples)
        CuadNuevo = (Cuad[0],direccionSalto,'','')
        Cuadruplos[indice]=CuadNuevo
    else:
        CuadNuevo = (Cuad[0],Cuad[1],direccionSalto,'')
        Cuadruplos[indice]=CuadNuevo
      
def p_ProgPral(p):
    'ProgPral : PROGRAM id DosPuntos PrimerCuad Var Sub RellenaPrimerCuad B END'

def p_PrimerCuad(p):
    'PrimerCuad : Vacio'
    creaCuadruplo('goto')

def p_RellenaPrimerCuad(p):
    'RellenaPrimerCuad : Vacio'
    Rellena(0,cont)

def p_Vacio(p):
    'Vacio : '

def p_Var(p):
    '''Var : V
            | Vacio'''

def p_Sub(p):
    '''Sub : Vacio
            | P Sub'''

def p_V(p):
    '''V : DIM IDrepCrear of Type PuntoYComa
            | DIM IDrepCrear of Type PuntoYComa V'''

def p_IDrepCrear(p):
    '''IDrepCrear : id
            | id Coma IDrepCrear'''
    global tablaVariables
    global posVar
    tablaVariables.append(p[1])
    tablaValores.append('U')
    posVar = posVar + 1

def p_IDrepOUT(p):
    '''IDrepOUT : idOUT
            | idOUT Coma IDrepOUT'''

def p_idOUT(p):
    'idOUT : id'
    global PilaOperandos

    PilaOperandos.append(p[1])
    creaCuadruplo('outputV')

def p_IDrepInput(p):
    '''IDrepInput : idInput
                | idInput Coma IDrepInput'''
    
def p_idInput(p):
    'idInput : id'

    creaCuadruplo('input')
    idDeInput = p[1]
    Rellena(cont-1,idDeInput)

def p_Type(p):
    '''Type : double
            | word
            | matrixDeclaration sacaMatrices'''
    global posVar
    global posTipo
    global tablaTipo
    while posTipo < posVar :
            tablaTipo.append(p[1])
            posTipo = posTipo + 1

def p_matrixDeclaration(p):
    'matrixDeclaration : matrix size CorcheteA Decnumsize CorcheteC'
    
def p_sacaMatrices(p):
    'sacaMatrices : Vacio'


    #print("tamaño lista", len(tablaVariables))
    i = len(tablaVariables) -1

    while i >= 0:
        posPalMatrix = tablaTipo[i].find('matrix')
        if posPalMatrix != -1 :
            #print ("si hay", posPalMatrix, tablaTipo[i], tablaVariables[i] )
            findComma = tablaTipo[i].find(',')
            primerCorchete = tablaTipo[i].find('[')
            segundoCorchete = tablaTipo[i].find(']')
            tipoObtenido =  tablaTipo[i]
            if findComma == -1:
                
                numero1 = tipoObtenido[primerCorchete+1:segundoCorchete]
                #print("Una dimension", numero1)
                creaMatrizUno(numero1)

            else:
                numero1 = tipoObtenido[primerCorchete+1:findComma]
                numero2 = tipoObtenido[findComma+1:segundoCorchete]
                #print("dos domensiones",numero1,numero2)
                creaMatrizDos(numero1,numero2)

        i -= 1

def creaMatrizUno(tam):
    global tablaMatricesValores
    global tablaMatrices
    global tablaVariables
    global tablaTipo
    global tablaValores

    nombreMatriz = tablaVariables.pop()
    basura = tablaTipo.pop()
    x = 0
    while x < int(tam):
        variableGuardar = nombreMatriz+'['+ str(x)+']'
        tablaMatrices.append(variableGuardar)
        tablaMatricesValores.append('U')
        x += 1

def creaMatrizDos(tam1, tam2):
    global tablaMatricesValores
    global tablaMatrices
    global tablaVariables
    global tablaTipo
    global tablaValores

    nombreMatriz = tablaVariables.pop()
    basura = tablaTipo.pop()
    x = 0
    while x < int(tam1):
        y = 0
        while y < int(tam2):
            variableGuardar = nombreMatriz+'['+ str(x)+','+str(y)+']'
            tablaMatrices.append(variableGuardar)
            tablaMatricesValores.append('U')
            y += 1
        x += 1

def p_Decnumsize(p):
    '''Decnumsize : numero Vacio
            | numero Coma numero'''
    if p[2] == ',':
        tam1 = str(p[1])
        tam2 = str(p[3])
        tamMatrix = "matrix" + '[' + tam1 + ',' + tam2 + ']'
    else :
        tam1 = str(p[1])
        tamMatrix = "matrix" + '[' + tam1 + ']'
    
    global posVar
    global posTipo
    global tablaTipo
    while posTipo < posVar :
            tablaTipo.append(tamMatrix)
            posTipo = posTipo + 1

def p_P(p):
    'P : SUB PROCEDURE nombreRutina DosPuntos B CuadruploReturn PuntoYComa'

def p_nombreRutina(p):
    'nombreRutina : id'
    global tablaSubRutinas
    global tablaSubRutinasDirecciones
    
    idRutina = p[1]
    tablaSubRutinas.append(idRutina)
    tablaSubRutinasDirecciones.append(cont)

def p_CuadruploReturn(p):
    'CuadruploReturn : RETURN'

    creaCuadruplo('return')

def p_B(p):
    'B : BEGIN Srep'

def p_Srep(p):
    '''Srep : S
            | S Srep'''

def p_S(p):
    '''S : letSintaxis PuntoYComa
            | IF ParentesisA E ParentesisC paso1IF THEN Srep Elsop ENDIF paso3IF PuntoYComa 
            | INPUT IDrepInput PuntoYComa
            | WHILE paso1WHILE ParentesisA E ParentesisC paso2WHILE Srep WEND paso3WHILE PuntoYComa
            | DO paso1DO Srep LOOP ParentesisA E ParentesisC paso2DO PuntoYComa
            | FOR ParentesisA letSintaxis paso1FOR PuntoYComa E paso2FOR PuntoYComa letSintaxis ParentesisC paso3FOR Srep NEXT paso4FOR PuntoYComa
            | GOSUB gosubCuad PuntoYComa
            | Gato miString Gato
            | OUTPUT Outopt PuntoYComa'''

def p_gosubCuad(p):
    'gosubCuad : id'
    creaCuadruplo('gosub')
    indiceRutina = tablaSubRutinas.index(p[1])
    direccionRutina = tablaSubRutinasDirecciones[indiceRutina]
    Rellena(cont-1,direccionRutina)

def p_paso1FOR(p):
    'paso1FOR : Vacio'

    global PilaSaltos
    global cont

    PilaSaltos.append(cont)
    
def p_paso2FOR(p):
    'paso2FOR : Vacio'
    
    global PilaSaltos
    global cont

    creaCuadruplo('gotoF')
    PilaSaltos.append(cont-1)
    creaCuadruplo('goto')
    PilaSaltos.append(cont-1)
    PilaSaltos.append(cont)

def p_paso3FOR(p):
    'paso3FOR : Vacio'
    
    global PilaSaltos
    global cont
   
    POPTOP = PilaSaltos.pop()
    POPTOPMENOS1 = PilaSaltos.pop()
    POPTOPMENOS2 = PilaSaltos.pop()
    POPTOPMENOS3 = PilaSaltos.pop()

    PilaSaltos.append(POPTOPMENOS2)
    PilaSaltos.append(POPTOP)
    
    creaCuadruplo('goto')
    Rellena(cont-1,POPTOPMENOS3)

    Rellena(POPTOPMENOS1,cont)

def p_paso4FOR(p):
    'paso4FOR : Vacio'

    global PilaSaltos
    global cont

    DIR = PilaSaltos.pop()

    creaCuadruplo('goto')
    Rellena(cont-1,DIR)

    DIR = PilaSaltos.pop()
    Rellena(DIR,cont)

def p_letSintaxis(p):
    'letSintaxis : LET letid matriz DosPuntosIgual E Cuadruploigualacion'
    
def p_paso1WHILE(p):
    'paso1WHILE : Vacio'

    global PilaSaltos

    #Push pila de saltos despues del WHILE
    PilaSaltos.append(cont)

def p_paso2WHILE(p):
    'paso2WHILE : Vacio'

    global PilaSaltos

    creaCuadruplo('gotoF')

    #push a pila de saltos
    PilaSaltos.append(cont-1)

def p_paso3WHILE(p):
    'paso3WHILE : Vacio'
    
    global PilaSaltos
    
    Dir2 = PilaSaltos.pop()
    Dir1 = PilaSaltos.pop()

    #Se crea cuadruplo goto
    creaCuadruplo('goto')

    #Se rellena el cuadruplo generado
    Rellena(cont-1, Dir1)

    #se rellena el cuadruplo gotoF pasado
    Rellena(Dir2, cont)

def p_paso1DO(p):
    'paso1DO : Vacio'

    global PilaSaltos

    #Push pila de saltos despues del DO
    PilaSaltos.append(cont)

def p_paso2DO(p):
    'paso2DO : Vacio'

    global PilaSaltos
    global Cuadruplos

    #Push pila de saltos despues del DO
    creaCuadruplo('gotoV')

    # Se rellena cuadruplo creado con la direccion de retorno
    DIR = PilaSaltos.pop()
    Rellena(len(Cuadruplos)-1,DIR)

def p_paso3IF(p):
    'paso3IF : Vacio'
    DIR = PilaSaltos.pop()
    Rellena(DIR,cont)

def p_paso1IF(p):
    'paso1IF : Vacio'
    creaCuadruplo('gotoF')
    
    global PilaSaltos

    # se guarda posicion gotoF
    PilaSaltos.append(cont-1)

def p_Cuadruploigualacion(p):
    'Cuadruploigualacion : Vacio'
    #global PilaOperandos
    #print(PilaOperandos.pop())
    creaCuadruplo(':=')

def p_letid(p):		
	'letid : id'
	global PilaOperandos
	PilaOperandos.append(p[1])
			
def p_E(p):
    '''E : ES Mayor ES
            | ES Menor ES
            | ES MayorIgual ES
            | ES MenorIgual ES
            | ES Igual ES
            | ES Diferente ES
            | ES'''
    if (len(p) > 2):
        creaCuadruplo(p[2])    

def p_ES(p):
    '''ES : T
            | ES Mas T
            | ES Menos T
            | ES OR T '''
    if (len(p) > 2):
        creaCuadruplo(p[2])   

def p_T(p):
    '''T : F 
            | T Por F
            | T AND F
            | T Entre F
            | T Potencia F
            | T NOT F'''
    if (len(p) > 2):
        creaCuadruplo(p[2])   

def p_F(p):
    '''F : id
            | id CorcheteA Erep CorcheteC 
            | numero
            | ParentesisA E ParentesisC'''
    
    global tablaVariables
    global PilaOperandos
    global operandoMatriz
    global DosDimensiones


    if operandoMatriz:
        if DosDimensiones :
            print(PilaOperandos[len(PilaOperandos)-1])
            print(PilaOperandos[len(PilaOperandos)-2])
            num2 = PilaOperandos.pop()
            num1 = PilaOperandos.pop()
            if type(num1) is int:
                num1 = str(num1)
            if type(num2) is int:
                num2 = str(num2)
            operandoAgregar = p[1]+'['+num1+','+num2+']'
            PilaOperandos.append(operandoAgregar)
        else:
            print(PilaOperandos[len(PilaOperandos)-1])
            num1 = PilaOperandos.pop()
            if type(num1) is int:
                num1 = str(num1)
            operandoAgregar = p[1]+'['+num1+']'
            PilaOperandos.append(operandoAgregar)
    else:
        if p[1] in tablaVariables :
            #indiceID = tablaVariables.index(p[1])
            #newOperand = '$' + str(indiceID)
            PilaOperandos.append(p[1])
        else :
            #newOperand = 'n' + str(p[1])
            PilaOperandos.append(p[1])

    operandoMatriz = False
    DosDimensiones = False

def p_Erep(p):
    '''Erep : E Vacio
            | E Coma E'''

    global operandoMatriz
    global DosDimensiones
    operandoMatriz = True

    if p[2]== ',':
        DosDimensiones = True
    
def p_matriz(p):
    '''matriz : Vacio
            | CorcheteA Erep CorcheteC'''

    global operandoMatriz
    global DosDimensiones


    if operandoMatriz:
        if DosDimensiones :
            num2 = PilaOperandos.pop()
            num1 = PilaOperandos.pop()
            variable =PilaOperandos.pop()
            if type(num1) is int:
                num1 = str(num1)
            if type(num2) is int:
                num2 = str(num2)
            operandoAgregar = variable+'['+num1+','+num2+']'
            PilaOperandos.append(operandoAgregar)
        else:
            print(PilaOperandos[len(PilaOperandos)-1])
            num1 = PilaOperandos.pop()
            variable =PilaOperandos.pop()
            if type(num1) is int:
                num1 = str(num1)
            operandoAgregar = variable+'['+num1+']'
            PilaOperandos.append(operandoAgregar)
    operandoMatriz = False
    DosDimensiones = False
    
def p_numsize(p):
    '''numsize : numero Vacio
            | numero Coma numero'''

    global PilaOperandos
	
    #print("si entró")
    #print("Pila de operandos",PilaOperandos)
    if (p[2] == ','):
        #doble
        variable = PilaOperandos.pop()
        PilaOperandos.append(variable+'['+str(p[1])+','+str(p[3])+']')
    else:
        #uno
        variable = PilaOperandos.pop()
        PilaOperandos.append(variable+'['+str(p[1])+']')
    #print("Pila de operandos",PilaOperandos)

def p_Elsop(p):
    '''Elsop : Vacio
            | ELSE paso2IF Srep'''

def p_paso2IF(p):
    'paso2IF : Vacio'
    creaCuadruplo('goto')

    global PilaSaltos

     #Se rellena goto pasado
    DIR = PilaSaltos.pop()
    Rellena(DIR,cont)
    PilaSaltos.append(cont-1)

def p_Outopt(p):
    '''Outopt : IDrepOUT
            | Comillas miStringOut Comillas'''
    global stringOutput
    
    if p[1] == '"':
        creaCuadruplo('outputS')
        stringOutput = ''

def p_miString(p):
    '''miString : Vacio
                | id miString
                | DosPuntos miString
                | PuntoYComa miString
                | Coma miString
                | CorcheteA miString
                | CorcheteC miString
                | numero miString
                | DosPuntosIgual miString
                | ParentesisA miString
                | ParentesisC miString
                | Comillas miString
                | Mayor miString
                | Menor miString
                | MayorIgual miString
                | MenorIgual miString
                | Igual miString
                | Diferente miString
                | Mas miString
                | Menos miString
                | Por miString
                | Entre miString
                | Potencia miString
                | GuionBajo miString 
                | SignoInterr miString'''

def p_miStringOut(p):
    '''miStringOut : Vacio
                | id miStringOut
                | DosPuntos miStringOut
                | PuntoYComa miStringOut
                | Coma miStringOut
                | CorcheteA miStringOut
                | CorcheteC miStringOut
                | numero miStringOut
                | DosPuntosIgual miStringOut
                | ParentesisA miStringOut
                | ParentesisC miStringOut
                | Mayor miStringOut
                | Menor miStringOut
                | MayorIgual miStringOut
                | MenorIgual miStringOut
                | Igual miStringOut
                | Diferente miStringOut
                | Mas miStringOut
                | Menos miStringOut
                | Por miStringOut
                | Entre miStringOut
                | Potencia miStringOut
                | GuionBajo miStringOut 
                | Gato miStringOut
                | SignoInterr miStringOut '''
    global stringOutput

    if p[1] != None:
        stringOutput = str(p[1]) + ' ' + stringOutput

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

#Seccion Ejecutor
def RepresentsInt(number):
    try: 
        int(number)
        return True
    except ValueError:
        return False

def RepresentsFloat(number):
    try: 
        float(number)
        return True
    except ValueError:
        return False

def ValorOperandos(operando):
    global tablaVariables
    global tablaTipo
    global PilaOperandos
    global AvailTemp
    global Cuadruplos
    global posVar
    global posTipo
    global cont
    global PilaSaltos
    global tablaValores
    global ValoresTemporales
    global tablaMatrices
    global tablaMatricesValores
    global tablaSubRutinas
    global tablaSubRutinasDirecciones
    global PilaOperacion
    global stringOutput


    #print("Operando",operando)
    #Revisar si es un numero en formato string (indice de matriz)
    if RepresentsFloat(operando):
        Valor = float(operando)
    elif RepresentsInt(operando):
        Valor = int(operando)
    elif type(operando) is str:
        posCA=operando.find('[')
        if posCA == -1 :
            # Revisar si es temporal
            if operando[0] == '$':
                if len(operando) == 4:
                    indiceTemporal = 10-1
                else:
                    indiceTemporal = int(operando[2]) -1
                Valor = ValoresTemporales[indiceTemporal]
            #cuando es una variable
            else:  
                indiceVariable = tablaVariables.index(operando)
                Valor = tablaValores[indiceVariable]
        else:
            indiceVariable = tablaMatrices.index(operando)
            Valor = tablaMatricesValores[indiceVariable]
     # es valor numerico
    else:
        Valor = operando
    return Valor

def AsignarValor(operando,Valor):
    global tablaVariables
    global tablaTipo
    global PilaOperandos
    global AvailTemp 
    global Cuadruplos
    global posVar
    global posTipo
    global cont
    global PilaSaltos
    global tablaValores
    global ValoresTemporales
    global tablaMatricesValores
    global tablaMatrices
    #print ("operand",operando, "valor", Valor)
    posCA=operando.find('[')
    if posCA == -1 :
        if operando[0] == '$':
            if len(operando) == 4:
                indiceTemporal = 10-1
            else:
                indiceTemporal = int(operando[2]) -1
            ValoresTemporales[indiceTemporal] = Valor
        else:
            #Obtener el tipo de valor que es el receptor
            indiceReceptor = tablaVariables.index(operando)
            tipoReceptor = tablaTipo[indiceReceptor]

            if Valor == 'U':
                sys.exit("Variable previamente no asignada")

            if tipoReceptor == 'double' :
                tablaValores[indiceReceptor]= float(Valor)
            elif tipoReceptor == 'word':
                Valor = float(Valor)
                tablaValores[indiceReceptor]= int(Valor)
    else:
        indiceVariable = tablaMatrices.index(operando)
        tablaMatricesValores[indiceVariable] = Valor
    
def obtenOperando(OP):
    global tablaVariables
    global tablaTipo
    global PilaOperandos
    global AvailTemp 
    global Cuadruplos
    global posVar
    global posTipo
    global cont
    global PilaSaltos
    global tablaValores
    global ValoresTemporales
    global tablaMatricesValores
    global tablaMatrices
    

    if isinstance(OP, str):
        posicionCA = OP.find('[')
        posicionCC = OP.find(']')
        
        if posicionCA == -1 :   
            Valor = OP
        elif isinstance(OP, str):
            posicionComa = OP.find(',')
            if posicionComa == -1:
                #simple
                numero1 = OP[posicionCA+1:posicionCC]
                if isinstance(numero1, str):
                    Valor1 = ValorOperandos(numero1)
                    if isinstance(Valor1, float):
                        Valor1 = int(Valor1)
                    Valor1 = str(Valor1)
                else:
                    if isinstance(numero1, float):
                        Valor1 = int(numero1)
                    Valor1 = str(numero1)
                
                Variable = OP[0:posicionCA]
                Variable = Variable+'['+Valor1+']'
                Valor = Variable
            else: 
                #doble
                numero1 = OP[posicionCA+1:posicionComa]
                numero2 = OP[posicionComa+1:posicionCC]

                if isinstance(numero1, str):
                    Valor1 = ValorOperandos(numero1)
                    if isinstance(Valor1, float):
                        Valor1 = int(Valor1)
                    Valor1 = str(Valor1)
                else:
                    if isinstance(numero1, float):
                        Valor1 = int(numero1)
                    Valor1 = str(numero1)
                
                if isinstance(numero2, str):
                    Valor2 = ValorOperandos(numero2)
                    if isinstance(Valor2, float):
                        Valor2 = int(Valor2)
                    Valor2 = str(Valor2)
                else:
                    if isinstance(numero2, float):
                        Valor2 = int(numero2)
                    Valor2 = str(numero2)
                
                Variable = OP[0:posicionCA]
                Variable = Variable+'['+Valor1+','+Valor2+']'
                Valor = Variable
    else:
        Valor = OP

    #print ("operando valor", OP, "valor", Valor)
    
    return Valor

def ejecutor():
    global tablaVariables
    global tablaTipo
    global PilaOperandos
    global AvailTemp 
    global Cuadruplos
    global posVar
    global posTipo
    global cont
    global PilaSaltos
    global tablaValores
    global ValoresTemporales
    global PilaOperacion

    i = 0

    print ('\nEjecutor')
    while i<cont :
        cuad = Cuadruplos[i]
        operacion = cuad[0]

        #Asignación
        if operacion == ':=':
            #print ('Asignación')

            #obtener operandos crudos
            Receptor = cuad[3]
            OP1 = cuad[1]
            
            #Se obtiene el operando traducido
            OP1 =  obtenOperando(OP1)
            Valor = ValorOperandos(OP1)

            #Se obtiene el receptor traducido
            Receptor =  obtenOperando(Receptor)

            # se asigna valor al receptor
            AsignarValor(Receptor,Valor)
        
        #Logica
        elif operacion == '<':
            #print ('Menor que')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)
            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0

            if Valor1 < Valor2 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)

        elif operacion == '>':
            #print ('Mayor que')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]


            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)
            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0

            if Valor1 > Valor2 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)

        elif operacion == '>=':
            #print ('Mayor igual')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0

            if Valor1 >= Valor2 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)

        elif operacion == '<=':
            #print ('Menor igual')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0

            if Valor1 <= Valor2 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)

        elif operacion == '=':
            #print ('Igualación')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0

            if Valor1 == Valor2 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)

        elif operacion == '<>':
            #print ('Diferente')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0

            if Valor1 != Valor2 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)
        
        #LOGIC GATES
        elif operacion == 'AND':
            #print ('AND')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0
            Valor3 = Valor1*Valor2
            if Valor3 > 0 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)

        elif operacion == 'OR':
            #print ('OR')
            
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = 0
            Valor3 = Valor1+Valor2
            if Valor3 > 0 :
                Resultado = 1
            
            AsignarValor(OP3,Resultado)

        #Operaciones
        elif operacion == '+':
            #print ('SUMA')
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)
            Resultado = Valor1+Valor2

            AsignarValor(OP3,Resultado)

        elif operacion == '*':
            #print ('Multiplicación')
            
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            
            if isinstance(Valor1, float) or isinstance(Valor2, float) :
                Resultado = Valor1*Valor2
            else:
                Resultado = int(Valor1*Valor2)

            AsignarValor(OP3,Resultado)

        elif operacion == '/':
            #print ('Division')
            
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)
            
            if isinstance(Valor1, float) or isinstance(Valor2, float) :
                Resultado = Valor1/Valor2
            else:
                Resultado = int(Valor1/Valor2)

            AsignarValor(OP3,Resultado)

        elif operacion == '^':
            #print ('Portencia')
            
            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = Valor1**Valor2

            AsignarValor(OP3,Resultado)

        elif operacion == '-':
            #print ('resta')

            OP1 = cuad[1]
            OP2 = cuad[2]
            OP3 = cuad[3]

            OP1 =  obtenOperando(OP1)
            OP2 =  obtenOperando(OP2)
            OP3 =  obtenOperando(OP3)

            Valor1 = ValorOperandos(OP1)
            Valor2 = ValorOperandos(OP2)

            Resultado = Valor1-Valor2

            AsignarValor(OP3,Resultado)

        #goto's
        elif operacion == 'goto':
            #print ('GOTO')
            salto = cuad[1]

            i = salto -1

        elif operacion == 'gotoF':
            #print ('GOTO Falso')

            condicion = cuad[1]
            salto = cuad[2]
            condicion = ValorOperandos(condicion)
            #print("Condicion", condicion, "salto", salto)
            if condicion == 0:
                i = salto - 1

        elif operacion == 'gotoV':
            #print ('GOTO Verdadero')

            condicion = cuad[1]
            salto = cuad[2]
            condicion = ValorOperandos(condicion)
            #print("Condicion", condicion, "salto", salto)
            if condicion >= 1:
                i = salto - 1

        elif operacion == 'gosub':
            #print("gosub")
            salto = cuad[1]
            PilaOperacion.append(i)

            i = salto -1

        elif operacion == 'return':
            #print("return")
            salto = PilaOperacion.pop()
            i = salto

        elif operacion == 'input':
            #print('input')
            lectura = ""
            while lectura == "":
                lectura = input("Input : ")
            operando = cuad[1]
            #lectura = str(lectura)
            AsignarValor(operando,lectura)

        elif operacion == 'outputS':
            #print('outputS')
            StringImprimir = cuad[1]
            print('OutputS : ', StringImprimir)
        
        elif operacion == 'outputV':
            #print ('outputV')
            valorOutput = cuad[1]
            valorOutput = ValorOperandos(valorOutput)
            print('OutputV : ',valorOutput)
        i +=1

def imprimeResultados():
    global tablaVariables
    global tablaTipo
    global PilaOperandos
    global AvailTemp 
    global Cuadruplos
    global posVar
    global posTipo
    global cont
    global PilaSaltos
    global tablaValores
    global ValoresTemporales

    longitudTablaSimbolos = len(tablaVariables)
    print("\nTabla de símbolos")
    #print('Variables','\t\t','Tipo','\t\t\t','Valor')
    i = 0
    toTab = []
    while i < longitudTablaSimbolos:
        #print(tablaVariables[i],'\t\t\t',tablaTipo[i],'\t\t', tablaValores[i])
        toTab.append( [tablaVariables[i], tablaTipo[i],tablaValores[i]])
        i = i+1
    print (tabulate(toTab,headers = ['Variables','Tipo','Valor']))
    
    print("\nTabla de matrices: ")
    #print('Variables','\t\t\t','Valor')
    longitudTablaMatrices = len(tablaMatrices)
    i = 0
    toTab = []
    while i < longitudTablaMatrices:
        #print(tablaMatrices[i],'\t\t\t', tablaMatricesValores[i])
        toTab.append( [tablaMatrices[i], tablaMatricesValores[i]])
        i += 1
    print (tabulate(toTab,headers = ['Variables','Valor']))

    print("\nTabla de Subrutinas: ")
    longitudTablaSub = len(tablaSubRutinas)
    i = 0
    toTab = []
    while i < longitudTablaSub:
        toTab.append( [tablaSubRutinas[i], tablaSubRutinasDirecciones[i]])
        i += 1
    print (tabulate(toTab,headers = ['Nombre','Direccion']))

    print('\nOperandos :\t', PilaOperandos)
    print('Temporales :\t', AvailTemp)
    print('Valores Temporales :\t', ValoresTemporales)
    print('\nCuadruplos :\t')
    i = 0
    for Cuad in Cuadruplos:
        print(i,'\t',Cuad)
        i +=1

    print("\nContador", cont)

    #print(tablaValores)

# Seccion correr programa
def lee():
    f = open("Programa4.txt", "r")

    stringSalida = ''

    while True:
        line = f.readline()
        if not line:
            break
        else:
            # eliminar end lines
            posEndline = line.find('\n')
            if posEndline != -1:
                line = line[0:posEndline]
            
            #eliminar tabulaciones
            posTab = line.find('\t')
            while posTab != -1:
                longLine = len(line)
                line = line[posTab+1:longLine]
                posTab = line.find('\t')
            
            # Se concatena la linea filtrada
            stringSalida += line + ' '

    return stringSalida 

def reiniciaTodo():
    global tablaVariables
    global tablaTipo
    global PilaOperandos
    global AvailTemp
    global Cuadruplos
    global posVar
    global posTipo
    global cont
    global PilaSaltos
    global tablaValores
    global ValoresTemporales
    global tablaMatrices
    global tablaMatricesValores
    global tablaSubRutinas
    global tablaSubRutinasDirecciones
    global PilaOperacion
    global stringOutput

    stringOutput = ''
    PilaOperacion = []
    tablaVariables = [] 
    tablaTipo = []
    PilaOperandos = []
    AvailTemp = ['$t1', '$t2', '$t3', '$t4', '$t5','$t6', '$t7', '$t8', '$t9', '$t10']
    Cuadruplos = []
    posVar = 0
    posTipo = 0
    cont = 0
    PilaSaltos = []
    tablaValores = []
    ValoresTemporales = ['U','U','U','U','U','U','U','U','U','U']
    tablaMatrices = []
    tablaMatricesValores = []
    tablaSubRutinas = []
    tablaSubRutinasDirecciones = []

while True:
    # Start all in 0;s
    reiniciaTodo()

    try:
        prueba = input('\nEjecutar?: ')
    except EOFError:
        break
    if not prueba: continue
    if prueba == "NO" or prueba == "no":
        break
    else :
        CodigoInput = lee()
        #print(CodigoInput)
        parser.parse(CodigoInput)

    #imprimeResultados()

    ejecutor()
    #imprimeResultados()
    
    respuestaImprime = ''
    print("\nQuieres imprimir resultados?")
    while respuestaImprime == '':
        respuestaImprime = input('yes / no: ')
        if respuestaImprime == 'yes' or respuestaImprime == 'no':
            respuestaImprime = respuestaImprime
        else :
            respuestaImprime = ''
    
    if respuestaImprime == 'yes':
        imprimeResultados()
        
    