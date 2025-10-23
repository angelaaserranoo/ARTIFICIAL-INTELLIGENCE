"""
Autores: Natalia Rodríguez Navarro y Ángela Serrano Casas

Este módulo presenta el código que permite obtener la política óptima
para la calefacción (acción ON o acción OFF) dada la temperatura que se 
desea alcanzar. Es decir, se presentará la acción más factible desde 
cada uno de los estados posibles (del 16 a 25 grados).
Para ello, debe darse unos valores a las constantes temperatura deseada 
(TEMPERATURA_DESEADA), coste de encendido (COSTE_ON), coste de apagado 
(COSTE_OF) y el número de ciclos (N_CICLOS) que se desea alcanzar para 
obtener el valor de los estados con la Ecuación de Bellman. Si se desea,
también puede darse la ruta de los archivos .csv que guardan las tablas
de probabilidades de las dos acciones, con el fin de usar una distinta
a la nuestra (CSV_PROBS_ON y CSV_PROBS_OFF).
"""
import csv


#---------------------------------- VALORES MODIFICABLES ---------------------------------------

# Temperatura que se desea alcanzar (estado final)
TEMPERATURA_DESEADA = 22
# Coste de la acción "encender calefacción"
COSTE_ON = 6.7793
# Coste de la acción "apagar calefacción"
COSTE_OFF = 0.610137
# Ciclos que se desean para calcular la política óptima
# En el caso de indicar None, se harán todos los ciclos necesarios
# hasta converger
N_CICLOS = None
# Ruta al fichero csv que guarda las matrices con las probabilidades
CSV_PROBS_ON = "./Ficheros_adicionales/PROB_ON.csv"
CSV_PROBS_OFF = "./Ficheros_adicionales/PROB_OFF.csv"



#----------------------------- OBTENCIÓN DEL RESTO DE VARIABLES --------------------------------

def obtener_matrices_probs(csv_path: str) -> list:
    """
    Carga las probabilidades de una tabla en csv en una matriz
    """
    with open(csv_path, 'r') as file:
        csvreader = csv.reader(file)
        primero = True
        matriz = []
        for row in csvreader:
            linea = []
            for data in row:
                if primero:
                    primero = False
                    # Añadimos los estados como strings
                    linea.append(data)
                else:
                    # Añadimos las probabilidades como floats
                    linea.append(float(data))
            matriz.append(linea)

    return matriz

# Obtenemos las probabilidades de las acciones ON y OFF, y
# las guardamos en una matriz
matriz_ON = obtener_matrices_probs(CSV_PROBS_ON)
matriz_OFF = obtener_matrices_probs(CSV_PROBS_OFF)
# El valor de los estados en el ciclo 0 es "0", por lo que
# usaremos una lista con los valores inicializados a "0"
# en el while que calculará la política óptima
estados = len(matriz_ON)+1
lista_convergencia  = [0] * estados



#----------------------------- COMPROBACIÓN DE VARIABLES CORRECTAS -----------------------------

# Comprobamos que los valores que pasaremos al while son correctos
temperaturas_posibles = [16,16.5,17,17.5,18,18.5,19,19.5,20,20.5,21,21.5,
                         22,22.5,23,23.5,24,24.5,25]
if TEMPERATURA_DESEADA not in temperaturas_posibles:
    raise TypeError ("La temperatura deseada debe ser un real entre 16 y "
                     "25 con saltos de 0.5 en 0.5")
if type(COSTE_ON) != float and type(COSTE_ON) != int:
    raise TypeError ("El coste de la acción ON debe ser un real")
if type(COSTE_OFF) != float and type(COSTE_OFF) != int:
    raise TypeError ("El coste de la acción OFF debe ser un real")
if N_CICLOS and type(N_CICLOS) != int and N_CICLOS > 0:
    raise TypeError ("El número de ciclos debe ser un natural o None")



#----------------------------- CÁLCULO DE LA POLÍTICA ÓPTIMA -----------------------------------

lista_convergencia_temp = list()
lista_politica_optima = list()
ciclos_restantes = N_CICLOS
converge = False
# Seguiremos calculando hasta que converjan los valores o hasta llegar
# al número de ciclos indicado
while ((not converge) and ((not ciclos_restantes) or (ciclos_restantes > 0))):
    """
    Cálculo de la política óptima a partir de la ecuación de Bellman. Obtenemos 
    una lista que contiene las acciones óptimas por cada uno de los estados dada 
    la lista de valores de estados inicial, las matrices de probabilidades, los costes 
    de las acciones, los ciclos a ejecutar y la temperatura deseada
    """
    lista_convergencia_temp = ["VALORES ESTADOS: "]
    lista_politica_optima = ["PATH: "]

    # Por cada estado y acción obtendremos su lista de probabilidades
    for estado in range(len(matriz_ON)):
        # Evitamos la primera lista de la matriz ya que contiene los estados
        if estado != 0:
            v_on = 0
            v_off = 0
            lista_probs_ON = matriz_ON[estado]
            lista_probs_OFF = matriz_OFF[estado]

            # Calculamos el valor del estado con la acción ON
            for prob in range(len(lista_probs_ON)):
                # Evitamos las probabilidades que son 0 y el primer elemento
                # de la lista ya que contiene el estado
                if lista_probs_ON[prob] != 0 and prob != 0:
                    v_on += lista_convergencia[prob] * lista_probs_ON[prob]             
            v_on += COSTE_ON

            # Calculamos el valor del estado con la acción OFF
            for prob in range(len(lista_probs_OFF)):
                # Evitamos las probabilidades que son 0 y el primer elemento
                # de la lista ya que contiene el estado
                if lista_probs_OFF[prob] != 0 and prob != 0:
                    v_off += lista_convergencia[prob] * lista_probs_OFF[prob]    
            v_off += COSTE_OFF

            # Si no se indica el número de ciclos, redondeamos los valores
            # para asegurar que éstos converjan
            if not N_CICLOS:
                v_on = round(v_on, 10)
                v_off = round(v_off, 10)

            # El elemento 0 de la lista contiene el estado en el que nos encontramos
            if lista_probs_ON[0] != TEMPERATURA_DESEADA:
                # Si no estamos en el estado final, añadimos su nuevo valor
                # y la acción que ha llevado al valor menor (la óptima)
                if v_on <= v_off:
                    lista_convergencia_temp.append(v_on)
                    lista_politica_optima.append("ON")
                else:
                    lista_convergencia_temp.append(v_off)
                    lista_politica_optima.append("OFF")
            else:
                # Si estamos en el estado final, su valor siempre es 0
                lista_convergencia_temp.append(0)
                # Como indica el enunciado, al alcanzar esta temperatura
                # el termostatato deja de funcionar. Por lo que no realizamos
                # ninguna acción
                lista_politica_optima.append("TEMPERATURA DESEADA")
    
    # Volveremos a calcular hasta que llegar al ciclo establecido (en caso de 
    # haber sido indicado)
    if N_CICLOS:
        ciclos_restantes -= 1

    # Comprobamos si converge, en tal caso, se da el resultado directamente
    if (lista_convergencia == lista_convergencia_temp):
        converge = True
    else:
        # La lista de convergencia, ahora será la nueva que hemos calculado
        lista_convergencia = lista_convergencia_temp



#--------------------------------------- RESULTADOS --------------------------------------------

# Mostramos el resultado por pantalla (política óptima por cada estado)
print("\nTemperatura deseada: ", TEMPERATURA_DESEADA)
for i in range(len(lista_politica_optima)-1):
    # La primera línea de la matriz almacena los estados
    print("Estado: ", matriz_ON[0][i+1], " Política óptima: ", lista_politica_optima[i+1])
print("\n")




