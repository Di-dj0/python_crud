import socket

from distributed.utils_test import client

import database_handler as db

class CRUD:

    def __init__(self):
        self.database = db.database_handler()
        # AF_INET = IPV4; SOCK_STREAM = TCP
        self.listener = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM)
        self.listener.bind(('127.0.0.1', 50000))

    def awaitConnection(self):
        self.listener.listen(1)
        client_socket, _ = self.listener.accept()
        print("Client connected")
        self.processRequest(client_socket)
    
    def processRequest(self, client_socket:socket.socket):
        while(True):
            # the opcode is always the first byte
            opcode = client_socket.recv(1)

            if not opcode:
                break

            opcode = int.from_bytes(opcode, 'big')
            print("Opcode: ", opcode)

            match opcode:
                # add new employee
                case 1:
                    # the package will be built as follow
                    # name_size | name | age = 1B | sex = 1B | adr_size | adr | sec_size | sec | salary_size | salary
                    name_size = int.from_bytes(client_socket.recv(1), 'big')
                    name = client_socket.recv(name_size).decode()
                    age = int.from_bytes(client_socket.recv(1), 'big')
                    sex = client_socket.recv(1).decode()
                    adr_size = int.from_bytes(client_socket.recv(1), 'big')
                    adr = client_socket.recv(adr_size).decode()
                    sec_size = int.from_bytes(client_socket.recv(1), 'big')
                    sec = client_socket.recv(sec_size).decode()
                    sal_size = int.from_bytes(client_socket.recv(1), 'big')
                    sal = client_socket.recv(sal_size).decode()

                    print("Package received:", name, age, sex, adr, sec, sal)

                    id = self.database.add_new_employee(name, age, sex, adr, sec, sal)

                    if id is None:
                        id = -1
                    
                    msg = opcode.to_bytes(1, 'big') + id.to_bytes(1, 'big', signed=True)
                    client_socket.send(msg)

                # search
                case 2:
                    # package:
                    # id(1)
                    id = int.from_bytes(client_socket.recv(1), 'big')
                    print("Searching ID:", id)
                    data = self.database.search_employee(id)

                    if data == -1:
                        print("Not found")
                    else:
                        print("Found:", data)

                    # if we found an employee with the id we populate every var
                    if data != -1:
                        msg = opcode.to_bytes(1, 'big')
                        # id
                        msg += id.to_bytes(1, 'big')
                        # name
                        msg += len(data[1].encode()).to_bytes(1, 'big') + data[1].encode()
                        # age
                        msg += data[2].to_bytes(1, 'big')
                        # sex
                        msg += data[3].encode()
                        # adress
                        msg += len(data[4].encode()).to_bytes(1, 'big') + data[4].encode()
                        # sector
                        msg += len(data[5].encode()).to_bytes(1, 'big') + data[5].encode()
                        # salary
                        msg += len(data[6].encode()).to_bytes(1, 'big') + data[6].encode()
                    else:
                        msg = data.to_bytes(1, 'big', signed=True)
                    
                    client_socket.send(msg)

                case 3:
                    id = int.from_bytes(client_socket.recv(1), 'big')
                    print("Updating ID:", id)

                    name_size = int.from_bytes(client_socket.recv(1), 'big')
                    name = client_socket.recv(name_size).decode() if name_size > 0 else None
                    print("Name:", name)

                    # We need to treat the age as a special case because it is an int
                    mode = client_socket.recv(1).decode()
                    if mode == "1":
                        age = None
                    else:
                        age = int.from_bytes(client_socket.recv(1), 'big', signed=True)
                    print("Age:", age)

                    sex_size = int.from_bytes(client_socket.recv(1), 'big')
                    sex = client_socket.recv(1).decode() if sex_size > 0 else None
                    print("Sex", sex)

                    adr_size = int.from_bytes(client_socket.recv(1), 'big')
                    adr = client_socket.recv(adr_size).decode() if adr_size > 0 else None
                    print("Adr:", adr)

                    sec_size = int.from_bytes(client_socket.recv(1), 'big')
                    sec = client_socket.recv(sec_size).decode() if sec_size > 0 else None

                    print("Sec:", sec)

                    sal_size = int.from_bytes(client_socket.recv(1), 'big')
                    sal = client_socket.recv(sal_size).decode() if sal_size > 0 else None

                    print("Sal:", sal)

                    #Check if the employee exists
                    data = self.database.update_employee_data(id, name, age, sex, adr, sec, sal)

                    #If the employee was not found, we return -1 and if it was found it was probably updated
                    if data != -1:
                        data = 1
                        msg = data.to_bytes(1, 'big', signed=True)
                    else:
                        data = -1
                        msg = data.to_bytes(1, 'big', signed=True)

                    client_socket.send(msg)

                case 4:
                    id = int.from_bytes(client_socket.recv(1), 'big')
                    print("Updating ID:", id)

                    #First we need to check if the employee exists so then we can delete it
                    data = self.database.search_employee(id)

                    if data == -1:
                        print("Not found")
                        status = 'N'                                #Set a status in case of there is no employee with the given id
                        msg = status.encode()
                    else:
                        result = self.database.delete_employee_data(id)
                        print(result)
                        print(id)
                        if result == id:
                            print("Deleted:", id)
                            status = 'S'                            #Set a status in case of the employee was deleted
                            msg = status.encode()
                        else:
                            print("Something went wrong, employee was not deleted")
                            status = 'B'                            #Set a status in case of the employee not being deleted for any reason
                            msg = status.encode()

                    client_socket.send(msg)

                case 5:
                    # as we are returning all the data, we don't need any parameteres
                    data = self.database.return_all_employee_data()
                    msg = opcode.to_bytes(1, 'big')

                    # if we have any data
                    if data != -1:
                        # first we say how many information we are sending
                        print(len(data))
                        msg += len(data).to_bytes(1, 'big')

                        # then we print the data to log in the server side and create the msg
                        for info in data:
                            print(info)
                            # id
                            msg += info[0].to_bytes(1, 'big')
                            # name
                            msg += len(info[1].encode()).to_bytes(1, 'big') + info[1].encode()
                            # age
                            msg += info[2].to_bytes(1, 'big')
                            # sex
                            msg += info[3].encode()
                            # adress
                            msg += len(info[4].encode()).to_bytes(1, 'big') + info[4].encode()
                            # sector
                            msg += len(info[5].encode()).to_bytes(1, 'big') + info[5].encode()
                            # salary
                            msg += len(info[6].encode()).to_bytes(1, 'big') + info[6].encode()
                    
                    else:
                        print("No employee data found:", data)
                        msg += data.to_bytes(1, 'big', signed=True)
                        
                    client_socket.send(msg)


def main():
    c = CRUD()
    print("Started server")
    # this makes so that the client can connect and disconnect any time
    while True:
        c.awaitConnection()

if __name__ == "__main__":
    main()