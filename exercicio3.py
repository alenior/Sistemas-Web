# Escreva um programa para combinar valores em uma lista de dicionários.
lista = [{'item': 'item1', 'amount': 400}, {'item': 'item2', 'amount': 300}, {'item': 'item1', 'amount': 750}]
dicionario = {}
for item in lista:
    i = item['item']
    if i in dicionario:
        dicionario[i] += item['amount']
    else:
        dicionario[i] = item['amount']
print(dicionario)
