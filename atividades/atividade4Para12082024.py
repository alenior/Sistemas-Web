#  Escreva uma função em Python que recebe uma string e calcula o número de letras maiúsculas e minúsculas na mesma.
# String Exemplo: 'Ordem e Progresso'
# Resultado Esperado :
# No. de letras maiúsculas : 2
# No. de letras minúsculas : 13

def contar_maiusculas_minusculas(s):
    maiusculas = 0
    minusculas = 0

    for char in s:
        if char.isupper():
            maiusculas += 1
        elif char.islower():
            minusculas += 1

    print(f"No. de letras maiúsculas: {maiusculas}")
    print(f"No. de letras minúsculas: {minusculas}")


# Exemplo de uso
string_exemplo = 'Ordem e Progresso'
contar_maiusculas_minusculas(string_exemplo)
