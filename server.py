import re
import cherrypy
import os
import json

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
    @cherrypy.tools.json_in()
    def adicionar(self, **kwargs):

        # Added an obj data to work with jsons
        data = cherrypy.request.json

        keys_required = {'name','age','sex','adress','sector','salary'}


        # Check if all keys are in kwargs
        if not keys_required.issubset(data.keys()):
            missing_keys = keys_required - set(data.keys())
            raise cherrypy.HTTPError(400, f"Missed one or more requered keys: {', '.join(missing_keys)}")

        if  searchString(numbers_regex, str(data.get('name'))) is not None and \
            searchString(letters_and_symbols_regex, str(data.get('age'))) is not None and \
            searchString(numbers_regex, str(data.get('sector'))) is not None and \
            searchString(letters_and_symbols_regex, str(data.get('salary'))) is not None and \
            (data.get('sex') == 'M' or data.get('sex') == 'F'):

            # Verify simple gramatic errors
            try:
                age = int(data['age'])
                salary = float(data['salary']) 
            except ValueError:
                raise cherrypy.HTTPError(422, "Age and Salary must be numbers")

            id_recebido = self.database.add_new_employee(
                data['name'], 
                age,
                data['sex'], 
                data['adress'], 
                data['sector'], 
                salary
                )

            if id_recebido is not None:
                cherrypy.response.status = "201"
                cherrypy.response.headers['Content-Type'] = 'application/json'
                return json.dumps({"message": f"Successul insertion for user {id_recebido}."}).encode('utf-8')
            else:
                raise cherrypy.HTTPError(500, "Erro in trying to insert user.")
            
        else:
            # This is used to build a more specific error message using our regexes
            errors = []
            if searchString(numbers_regex, str(data.get('age'))) is not None:
                errors.append("Invalid Name (Has numbers).")

            if searchString(letters_and_symbols_regex, str(data.get('age'))) is not None:
                errors.append("Invalid Age (Must be a number).")
            
            if data.get('sex') not in ['M', 'F']:
                errors.append("Invalid Gender (Mus be M or F).")
            
            if searchString(numbers_regex, str(data.get('sector'))) is None:
                 errors.append("Invalid Sector (Has numbers).")
            
            if searchString(letters_and_symbols_regex, str(data.get('salary'))) is not None:
                 errors.append("Invalid Salary (Must be a number).")
            
            raise cherrypy.HTTPError(422, f"One or more values are incorrect: {'; '.join(errors)}")

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

    @cherrypy.tools.json_in()
    def atualizar(self, id, **kwargs):

        data_to_update = cherrypy.request.json

        if not id.isdigit():
            raise cherrypy.HTTPError(400, "Invalid ID Format (Must be an Integer).")

        id_update = int(id)
        existing_data = self.database.search_employee(id_update)

        if existing_data == -1 or existing_data is None:
            raise cherrypy.HTTPError(404, "Employee not found")

        # Same logi as in Add()
        validation_errors = []
        if 'name' in data_to_update and searchString(numbers_regex, str(data_to_update['name'])) is None:
            validation_errors.append("Invalid value for 'name' (Has numbers).")

        if 'age' in data_to_update:
            if searchString(letters_and_symbols_regex, str(data_to_update['age'])) is None: # Deve ser número
                 validation_errors.append("Invalid value for 'age' (Must be a number).")
            else:
                try:
                    data_to_update['age'] = int(data_to_update['age'])
                except ValueError:
                    validation_errors.append("'age' must be a valid integer.")

        if 'sex' in data_to_update and data_to_update['sex'] not in ['M', 'F']:
            validation_errors.append("Invalid value for 'sex' (Must be M or F).")
        
        if 'sector' in data_to_update and searchString(numbers_regex, str(data_to_update['sector'])) is None: # Não deve ter números
            validation_errors.append("Invalid value for 'sector' (Has numbers).")

        if 'salary' in data_to_update:
            if searchString(letters_and_symbols_regex, str(data_to_update['salary'])) is None: # Deve ser número
                validation_errors.append("Invalid value for 'salary' (Must be a number).")
            else:
                try:
                    data_to_update['salary'] = float(data_to_update['salary'])
                except ValueError:
                    validation_errors.append("'salary' must be a valid number.")

        if validation_errors:
            raise cherrypy.HTTPError(422, f"Invalid values: {'; '.join(validation_errors)}")

        updated_name = data_to_update.get('name', existing_data[1])
        updated_age = data_to_update.get('age', existing_data[2])
        updated_sex = data_to_update.get('sex', existing_data[3])
        updated_adress = data_to_update.get('adress', existing_data[4]) 
        updated_sector = data_to_update.get('sector', existing_data[5])
        updated_salary = data_to_update.get('salary', existing_data[6]) 

        success = self.database.update_employee_data( # Adicionei id_update aqui
            id_update, 
            updated_name, 
            int(updated_age),
            updated_sex, 
            updated_adress, 
            updated_sector, 
            float(updated_salary)
        )

        if success is not None:
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return json.dumps({"message": f"Employee: {id_update} updated."}).encode('utf-8')
        else:
            raise cherrypy.HTTPError(500, "Error updating the employee data!")

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
    
    # PATCH because it is partial update
    despachante.connect(name='atualizaEmpregado', route='/employee_data/:id', controller=c,
                    action='atualizar', conditions=dict(method=['PATCH']))
    
    despachante.connect(name='deletaEmpregado', route='/employee_data/:id', controller=c,
                        action='deletar', conditions=dict(method=['DELETE']))

    # conf = {'/': {'request.dispatch': despachante}}
    
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(), # MethodDispatcher to map HTTP verbs
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')] # Default Content-Type
        }
    }

    config_app = {'/': {'request.dispatch': despachante}}

    cherrypy.tree.mount(root=None, config=config_app)
    cherrypy.config.update({'server.socket_port': 8080})

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == "__main__":
    main()