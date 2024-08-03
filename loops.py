numeros = [1, 2, 3, 4, 5]
for numero in numeros:
    print(numero)
print("")

for i in range(10):
    if i == 5:
        break
    print(i)
print("")

for x in range(5):
    print(x)
else:
    print("Loop for concluído.")
print("")

contador = 0
while contador < 5:
    print(contador)
    contador += 1
else:
    print("Loop while concluído.")
