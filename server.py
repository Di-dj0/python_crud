
import Pyro5
import Pyro5.api
import Pyro5.core
import Pyro5.server
import Pyro5.nameserver
import objects
import database_handler as db

@Pyro5.server.expose

class CRUD:

    def __init__(self):
        self.database = db.database_handler()

    def adicionar(self, employee: objects.CRUD_object) -> int:
        id = self.database.add_new_employee(employee.name, employee.age, employee.sex, employee.adress, employee.sector, employee.salary)
        return id

    def buscar(self, id:int):
        data = self.database.search_employee(id)
        if data is not None:
            employee = objects.CRUD_object(data[1], data[2], data[3], data[4], data[5], data[6], id)
            return employee
        else:
            return None

    def atualizar(self, id:int, employee: objects.CRUD_object):
        data = self.database.search_employee(id)
        if data is not None:
            update = self.database.update_employee_data(employee.name, employee.age, employee.sex, employee.adress, employee.sector, employee.salary)
            if update is not None:
                employee = objects.CRUD_object(update[1], update[2], update[3], update[4], update[5], update[6], id)
                return employee
            else:
                return None
        else:
            return None

    def deletar(self, id:int):
        data = self.database.search_employee(id)
        if data is not None:
            result = self.database.delete_employee_data(id)
            if result == id:
                return True
            else:
                return False
        else:
            return None
        
    def buscarTudo(self):
        data = self.database.return_all_employee_data()
        search_result = []
        if data is not None:
            for employee in data:
                print(employee)
                search_result.append(objects.CRUD_object(employee[1], employee[2], employee[3], employee[4], employee[5], employee[6], employee[0]))
            print(search_result)
            return search_result
        else:
            return None

def main():
    c = CRUD()
    daemon = Pyro5.server.Daemon()
    localizacao = daemon.register(c)

    Pyro5.api.register_class_to_dict(objects.CRUD_object, objects.convert_to_dict)
    Pyro5.api.register_dict_to_class('objects.CRUD_object', objects.convert_to_object)

    ns = Pyro5.core.locate_ns()
    ns.register("CRUD", localizacao)
    # initiate the main loop for requests
    daemon.requestLoop()

if __name__ == "__main__":
    main()