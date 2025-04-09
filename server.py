import socket
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

def main():
    c = CRUD()
    print("Started server")
    # this makes so that the client can connect and disconnect any time
    while True:
        c.awaitConnection()

if __name__ == "__main__":
    main()