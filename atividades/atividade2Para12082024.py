# Escreva um programa que retorna se dois dicionários possuem o mesmo item.
# Exemplo: {'key1': 1, 'key2': 3, 'key3': 2}, {'key1': 1, 'key2': 2}
# Resultado: key1: 1 está presente em x e y

def verificar_itens_comuns(dict1, dict2):
    itens_comuns = {}
    for chave, valor in dict1.items():
        if chave in dict2 and dict2[chave] == valor:
            itens_comuns[chave] = valor

    if itens_comuns:
        for chave, valor in itens_comuns.items():
            print(f"{chave}: {valor} está presente em ambos os dicionários.")
    else:
        print("Não há itens comuns nos dicionários.")


# Exemplos de uso
dict1 = {'key1': 1, 'key2': 3, 'key3': 2}
dict2 = {'key1': 1, 'key2': 2}

verificar_itens_comuns(dict1, dict2)
