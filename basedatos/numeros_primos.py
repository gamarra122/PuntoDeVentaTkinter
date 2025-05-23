def es_primo(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

inicio = int(input("Ingresá el número desde el que querés empezar a buscar primos: "))
contador = 0
numero = inicio

while contador < 20:
    if es_primo(numero):
        print(numero)
        contador += 1
    numero += 1


