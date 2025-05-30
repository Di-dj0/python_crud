import re
import cherrypy

import database_handler as db

numbers_regex = r'-?\d+(?:\.\d+)?'
letters_and_symbols_regex = r'[A-Za-z!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]'

def searchString(regex, input):
    # here we search the input string for the specified regex
    match = re.search(regex, input)
    # if a match is found
    if match:
        input = None
    return input

@cherrypy.expose

class CRUD:

    def __init__(self):
        print("Started server")
        self.database = db.database_handler()

    #Now functions receive parameters as kwargs so we are able to pass parameters dynamically
    def adicionar(self, **kwargs):
        keys = {'name','age','sex','adress','sector','salary'}
        # Check if all keys are in kwargs
        if set(kwargs.keys()).issuperset(keys):
            if searchString(numbers_regex, kwargs['name']) is not None and searchString(numbers_regex,kwargs['age']) is not None and searchString(numbers_regex, kwargs['sector']) is not None and searchString(letters_and_symbols_regex, kwargs['salary']) is not None and (kwargs['sex'] == 'M' or kwargs['sex'] == 'F'):
                id_recebido = self.database.add_new_employee(kwargs['name'], int(kwargs['age']), kwargs['sex'], kwargs['adress'], kwargs['sector'], kwargs['salary'])
                if id_recebido is not None:
                    cherrypy.response.status = "201"
                    return f"<div>Usuário inserido com ID {id_recebido}.</div>"
                else:
                    raise cherrypy.HTTPError(500, "Failed to insert employee data into the database")
            else:
                raise cherrypy.HTTPError(422, 'One of the values is not valid')
        else:
            raise cherrypy.HTTPError(400,"You missed one or more keys")

    def buscar(self, **kwargs):
        if 'id' in kwargs.keys():

            if not kwargs['id'].isdigit():
                raise cherrypy.HTTPError(400, "Invalid 'id' format. Must be an integer.")
            employee_data = self.database.search_employee(int(kwargs['id']))

            if employee_data != -1:
                mensagem = f'<div>ID: {employee_data[0]} + \nName:{employee_data[1]} + \nAge:   {employee_data[2]}  \nSex: {employee_data[3]}  \nAddress:  {employee_data[4]} \nSector: {employee_data[5]}  \nSalary: {employee_data[6]} </div>'
                return mensagem
            else:
                raise cherrypy.HTTPError(404, 'Employee not found')
        else:
            raise cherrypy.HTTPError(400, "You missed the 'id' key")

    #How to filter update data?
    def atualizar(self, **kwargs):
        keys = {'id', 'name', 'age', 'sex', 'adress', 'sector', 'salary'}

        invalid_keys = set(kwargs.keys()) - keys
        if invalid_keys:
            raise cherrypy.HTTPError(400, f"Invalid keys provided: {', '.join(invalid_keys)}")

        if 'id' not in kwargs.keys():
            raise cherrypy.HTTPError(400, "You missed the 'id' key")

        id_update = int(kwargs['id'])
        existing_data = self.database.search_employee(id_update)

        if existing_data == -1:
            raise cherrypy.HTTPError(404, "Employee not found")

        if 'name' in kwargs and searchString(numbers_regex, kwargs['name']) is not None:
            raise cherrypy.HTTPError(422, "Value not valid for 'name'")
        if 'age' in kwargs and searchString(numbers_regex, kwargs['age']) is not None:
            raise cherrypy.HTTPError(422, "Value not valid for 'age'")
        if 'sex' in kwargs and kwargs['sex'] not in ['M', 'F']:
            raise cherrypy.HTTPError(422, "Value not valid for 'sex'")
        if 'adress' in kwargs and searchString(numbers_regex, kwargs['adress']) is not None:
            raise cherrypy.HTTPError(422, "Value not valid for 'adress'")
        if 'sector' in kwargs and searchString(numbers_regex, kwargs['sector']) is not None:
            raise cherrypy.HTTPError(422, "Value not valid for 'sector'")
        if 'salary' in kwargs and searchString(letters_and_symbols_regex, kwargs['salary']) is not None:
            raise cherrypy.HTTPError(422, "Value not valid for 'salary'")

        # Use provided values or fallback to existing data
        updated_name = kwargs.get('name', existing_data[1])
        updated_age = int(kwargs.get('age', existing_data[2]))
        updated_sex = kwargs.get('sex', existing_data[3])
        updated_adress = kwargs.get('adress', existing_data[4])
        updated_sector = kwargs.get('sector', existing_data[5])
        updated_salary = kwargs.get('salary', existing_data[6])

        # Update the employee data
        updated_data = self.database.update_employee_data(
            updated_name, updated_age, updated_sex, updated_adress, updated_sector, updated_salary
        )

        if updated_data is not None:
            return f"<div>Empregado: {id_update} atualizado com sucesso.</div>"
        else:
            raise cherrypy.HTTPError(500, "Failed to update employee data")

    def deletar(self, **kwargs):
        if 'id' not in kwargs.keys():
            raise cherrypy.HTTPError(400, "You missed the 'id' key")
        id = int(kwargs['id'])

        if self.database.search_employee(id) == -1:
            raise cherrypy.HTTPError(404, "Employee not found")

        deleted_id = self.database.delete_employee_data(id)
        if deleted_id != -1:
            return f"<div>Empregado: {deleted_id} deletado com sucesso.</div>"
        else:
            raise cherrypy.HTTPError(500, "Failed to delete employee data")
        
    def buscarTudo(self):
        data = self.database.return_all_employee_data()
        mensagem = ['<div>Lista de empregados cadastrados:</div>']
        if data is not None:
            for employee_data in data:
                mensagem += '<div>ID: ' + str(employee_data[0]) + '\nName: ' + str(employee_data[1]) + '\nAge: ' + str(employee_data[2]) + '\nSex: ' + str(employee_data[3]) + '\nAddress: ' + str(employee_data[4]) + '\nSector: ' + str(employee_data[5]) + '\nSalary: ' + str(employee_data[6]) + '</div>'
            return mensagem
        else:
            #If there is no data, should we send response 204?
            return None

# simple function to clear the console by os
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')
clear()

def main():
    c = CRUD()
    despachante = cherrypy.dispatch.RoutesDispatcher()

    despachante.connect(name='Adicionar', route='/employee_data', controller=c,
                        action='adicionar', conditions=dict(method=['POST']))
    despachante.connect(name='buscarEmpregados', route='/employee_data', controller=c,
                        action='buscarTudo', conditions=dict(method=['GET']))
    despachante.connect(name='buscarEmpregado', route='/employee_data/:id', controller=c,
                        action='buscar', conditions=dict(method=['GET']))
    #PATCH because it is partial update
    despachante.connect(name='atualizaEmpregado', route='/employee_data/:id', controller=c,
                    action='atualizar', conditions=dict(method=['PATCH']))
    despachante.connect(name='deletaEmpregado', route='/employee_data/:id', controller=c,
                        action='deletar', conditions=dict(method=['DELETE']))

    conf = {'/': {'request.dispatch': despachante}}
    cherrypy.tree.mount(root=None, config=conf)
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == "__main__":
    main()