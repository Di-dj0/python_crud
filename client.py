import socket
import re

# we start creating the socket and option variable
# AF_INET = IPV4; SOCK_STREAM = TCP
client = socket.socket(socket.AF_NET, 
                       socket.SOCK_STREAM)
client.connect(('127.0.0.1', 50000))

option = None

def askInfo():
    # we created regexes for every data asked for the user
    numbers_regex = r'-?\d+(?:\.\d+)?'
    letters_and_symbols_regex = r'[A-Za-z!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]'
    name = input("Digite o nome do empregado\n")
    name = searchString(numbers_regex, name)

    age = input("Digite a idade\n")
    age = searchString(letters_and_symbols_regex, age)

    sex = input("Digite o sexo\n")
    if len(sex) > 1:
        while(len(sex) > 1):
            sex = input("O sexo deve ser sinalizado usando M ou F apenas!\n")
            sex = searchString(numbers_regex, sex)
    sex = searchString(numbers_regex, sex)

    adress = input("Digite o endereço\n")

    sector = input("Digite o setor\n")
    sector = searchString(numbers_regex, sector)

    salary = input("Digite o salário\n")
    salary = searchString(letters_and_symbols_regex, salary)

    return (name, age, sex, adress, sector, salary) 

def searchString(regex, input):
    # here we search the input string for the specified regex
    match = re.search(regex, input)
    # if a match is found
    if match:
        while(match):
            # ask for a new input
            input = input("Inconsistências foram encontradas!\n\
                        Favor digitar novamente.\n")
            match = re.search(regex, input)
    return input

def createRequest(opcode, id = None, name = None, age = None, sex = None, adress = None, sector = None, salary = None):
    msg = opcode.to_bytes(1, 'big')
    
    match opcode:
        case 1:
            msg += len(name.encode()).to_bytes(1, 'big') + name.encode()
            msg += age.to_bytes(1, 'big')
            msg += sex.encode()
            msg += len(adress.encode())

while option != 0:
    option = int(input("Selecione uma das opções abaixo\n\
                       1. Adicionar novo trabalhador\n\
                       \n\
                       0. Sair"))
    
    match option:
        case 1:
            name, age, sex, adress, sector, salary = askInfo()

