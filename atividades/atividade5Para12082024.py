# Escreva uma função em Python que retorna uma string reversa.
# Exemplo Entrada : "1234abcd"
# Exemplo Saída : "dcba4321"

def reverter_string(s):
    return s[::-1]


# Exemplo de uso
string_exemplo = "1234abcd"
resultado = reverter_string(string_exemplo)
print(resultado)
