import socket
import re
import os
import Pyro5
import Pyro5.client
import Pyro5.api
import objects

# simple function to clear the console by os
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')
clear()

# we created regexes for every data asked for the user
numbers_regex = r'-?\d+(?:\.\d+)?'
letters_and_symbols_regex = r'[A-Za-z!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]'

def askInfo():
    name = input("Digite o nome do empregado\n")
    name = searchString(numbers_regex, name)

    age = input("Digite a idade\n")
    if age == "":
        age = ""
    else:
        age = int(searchString(letters_and_symbols_regex, age))

    sex = input("Digite o sexo\n")
    if len(sex) > 1:
        while(len(sex) > 1):
            sex = input("O sexo deve ser sinalizado usando M ou F apenas!\n")
            sex = searchString(numbers_regex, sex)
        sex = searchString(numbers_regex, sex)

    adress = input("Digite o endereço\n")

    sector = input("Digite o setor\n").upper()
    sector = searchString(numbers_regex, sector).upper()

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


def main():

    Pyro5.api.register_class_to_dict(objects.CRUD_object, objects.convert_to_dict)
    Pyro5.api.register_dict_to_class('objects.CRUD_object', objects.convert_to_object)
    CRUD = Pyro5.client.Proxy("PYRONAME:CRUD")

    if CRUD._pyroBind():
        print('Now we have the remote object')
    else:
        print('For some reason we don\'t have the remote object')

    option = None
    while option != 0:
        option = int(input("Selecione uma das opções abaixo\
                        \n1. Adicionar novo empregado\
                        \n2. Procurar empregado por id\
                        \n3. Atualize os dados de um empregado através de ID\
                        \n4. Deletar empregado\
                        \n5. Mostrar empregados cadastrados\
                        \n\
                        \n0. Sair\n"))
        
        match option:
            case 1:
                name, age, sex, adress, sector, salary = askInfo()
                employee = objects.CRUD_object(name, age, sex, adress, sector, salary)
                id = CRUD.adicionar(employee)
                employee.id = id
                print(f"Empregado {employee.id} adicionado com sucesso!\n\)n")

            case 2:

                id = int(input("Digite o ID a ser procurado:\n"))
                employee = CRUD.buscar(id)
                if employee is not None:
                    print(employee.id, employee.name, employee.sex, employee.age, employee.adress, employee.sector, employee.salary)
                else:
                    print("Empregado não encontrado!\n\n")

            case 3:
                id = int(input("Digite o ID que deseja atualizar:\n"))
                print("Digite os dados que deseja atualizar, e para os demais pressione enter\n")
                name, age, sex, adress, sector, salary = askInfo()
                employee = objects.CRUD_object(name, age, sex, adress, sector, salary)
                updates = CRUD.atualizar(id, employee)
                if updates is not None:
                    print(f"Empregado {updates.id} atualizado com sucesso!\n")
                else:
                    print("O empregado não foi atualizado por motivos desconhecidos. Tente novamente!\n\n")

            case 4:
                id = int(input("Digite o ID que deseja deletar:\n"))
                employee = CRUD.deletar(id)
                if employee is not None:
                    print(f"Empregado {employee.id} deletado com sucesso!\n")
                else:
                    print("O empregado não foi deletado por motivos desconhecidos. Tente novamente!\n\n")

            case 5:
                #Busca todos aqui
                employees = CRUD.buscarTudo()



if __name__ == "__main__":
    main()