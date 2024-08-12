# Escreva um programa em Python que seleciona os itens ímpares em uma lista.
# Lista Exemplo : [1,5,7,3,10,14,21,22]
# Resultado: [1,5,7,3,21]

def selecionar_impares(lista):
    impares = [numero for numero in lista if numero % 2 != 0]
    return impares


# Exemplo de uso
lista_exemplo = [1, 5, 7, 3, 10, 14, 21, 22]
resultado = selecionar_impares(lista_exemplo)
print(resultado)
