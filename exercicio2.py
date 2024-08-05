# Escreva um programa em Python que conta o número de string com tamanho 2 ou mais e a primeira e último caracter da
# string são iguais.

lista = ['abc', 'xyz', 'aba', '1221']

strings = 0
for i in lista:
    if i[0] == i[-1]:
        strings += 1
print(strings)
