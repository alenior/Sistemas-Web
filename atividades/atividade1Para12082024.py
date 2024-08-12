# Escreva uma função em Python que recebe uma lista e retorna uma nova lista com os elementos únicos da lista inicial.
# Lista Exemplo : [1,2,3,3,3,3,4,5]
# Saída : [1, 2, 3, 4, 5]

listaExemplo = []
elemento = ''

while elemento != -1:
    elemento = int(input('Informe o novo número (-1 encerra): '))
    if elemento != -1:
        listaExemplo.append(int(elemento))
print(f'A lista dos elementos informados foi {listaExemplo}')
print('')

novaLista = []
for elemento in listaExemplo:
    if elemento not in novaLista:
        novaLista.append(elemento)
print(f'A nova lista fica: {novaLista}')
