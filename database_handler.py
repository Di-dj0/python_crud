import sqlite3

class database_handler:

    def __init__(self):
        # where is the database
        self.connection = sqlite3.connect("database.db")

        # create a cursor to handle sql code execution
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS employee_data(id INTEGER PRIMARY KEY, name, age, sex, adress, sector, salary)")
        self.connection.commit()
        
        # close the cursor
        cursor.close()

    def add_new_employee(self, name, age, sex, adress, sector, salary):
        # create a cursor to execute sql code
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO employee_data(name, age, sex, adress, sector, salary) VALUES(?, ?, ?, ?, ?, ?)", (name, age, sex, adress, sector, salary))

        # return the id of the last insertion
        if(cursor.rowcount > 0):
            id = cursor.lastrowid
        else:
            id = None

        # commit the changes to the database
        self.connection.commit()
        cursor.close()
        return id
    
    def search_employee(self, id):
        # create a cursor to execute sql code
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM employee_data WHERE id = ?", (id,)) # this needs a tuple
        
        # fetch from the cursor the info extracted from the database
        value = cursor.fetchone()
        
        # we don't need to commit here, just close the cursor
        cursor.close()
        return value
    
    def update_employee_data(self, id, name = None, age = None, sex = None, adress = None, sector = None, salary = None):
        # we can use the already created search_employee() function
        data = self.search_employee(id)

        # we only change the employee data if the data is found
        if(data is not None):
            # here we use a trick to change if the var is not None
            # if the var is None, we use the data extracted from the db
            # starting with 1 bc 0 is the id
            new_name = name if name else data[1]
            new_age = age if age else data[2]
            new_sex = sex if sex else data[3]
            new_adress = adress if adress else data[4]
            new_sector = sector if sector else data[5]
            new_salary = salary if salary else data[6]

            # now we create a cursor
            cursor = self.connection.cursor()
            cursor.execute("UPDATE employee_data SET name = ?, age = ?, sex = ?, adress = ?, sector = ?, salary = ? WHERE id = ?", (name, age, sex, adress, sector, salary, id))
            self.connection.commit()

            # here we use the rowcount to see if any employee data was change
            if(cursor.rowcount > 0):
                data = self.search_employee(id)
            else:
                data = None

            cursor.close()
            return data
        
    def delete_employee_data(self, id):
        # first we verify if the id exists
        if(not self.search_employee(id)):
            # if it dont, we return an error code
            return -2

        # we create a cursor to execute sql code
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM employee_data WHERE id = ?", (id,))
        self.connection.commit()

        # now we search for the employee data to verify the exclusion
        if(not self.search_employee(id)):
            value = id
        else:
            value = -1
        
        cursor.close()
        return value
