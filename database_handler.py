import sqlite3, threading

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
        # here we lock the thread for the sqlite implementation
        self.lock = threading.Lock()
        # and we allow coonections to use this thread
        self.connection = sqlite3.connect("database.db", check_same_thread=False)
        self._initialize_db()


    def _initialize_db(self):
        # used lock for all database operations
        with self.lock: 
            cursor = self.connection.cursor()
            try:
                # enable foreign key
                cursor.execute("PRAGMA foreign_keys = ON;")

                # create sectors table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sectors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    )
                """)

                # create employees table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        age INTEGER,
                        sex TEXT,
                        adress TEXT, 
                        salary REAL,
                        sector_id INTEGER,
                        FOREIGN KEY (sector_id) REFERENCES sectors(id)
                            ON DELETE SET NULL  -- If a sector is deleted, set employee's sector_id to NULL
                            ON UPDATE CASCADE   -- If a sector's id changes, update it in employees table
                    )
                """)
                self.connection.commit()
            finally:
                cursor.close()

    def _get_or_create_sector_id(self, sector_name):
        if not sector_name or not isinstance(sector_name, str) or not sector_name.strip():
            return None 
        
        sector_name_cleaned = sector_name.strip()
        cursor = self.connection.cursor()

        try:
            cursor.execute("SELECT id FROM sectors WHERE name = ?", (sector_name_cleaned,))
            row = cursor.fetchone()
            if row:
                # Sector exists
                return row[0]  
            else:
                # sector does not exist, attempt to create it
                try:
                    cursor.execute("INSERT INTO sectors (name) VALUES (?)", (sector_name_cleaned,))
                    return cursor.lastrowid
                
                except sqlite3.IntegrityError:
                    print(f"Race condition handled for sector: {sector_name_cleaned}")
                    cursor.execute("SELECT id FROM sectors WHERE name = ?", (sector_name_cleaned,))
                    row = cursor.fetchone()
                    return row[0] if row else None
                
        except sqlite3.Error as e:
            print(f"Error in _get_or_create_sector_id for '{sector_name_cleaned}': {e}")
            return None
        
        finally:
            cursor.close()

    # added the sector_id search to the method
    def add_new_employee(self, name, age, sex, adress, sector_name, salary):
        with self.lock:
            sector_id = self._get_or_create_sector_id(sector_name)
            if sector_id is None and sector_name is not None and sector_name.strip() != "":
                return None

            cursor = self.connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO employees (name, age, sex, adress, salary, sector_id) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, age, sex, adress, salary, sector_id))
                
                inserted_id = None
                if cursor.rowcount > 0:
                    inserted_id = cursor.lastrowid
                
                self.connection.commit()
                return inserted_id
            except sqlite3.Error as e:
                print(f"Database error in add_new_employee: {e}")
                # rollback on error
                self.connection.rollback()
                return None
            finally:
                cursor.close()
    
    def search_employee(self, employee_id):
        with self.lock:
            cursor = self.connection.cursor()
            try:
                # now we need to join the tables to search employees
                cursor.execute("""
                    SELECT e.id, e.name, e.age, e.sex, e.adress, s.name as sector_name, e.salary 
                    FROM employees e
                    LEFT JOIN sectors s ON e.sector_id = s.id
                    WHERE e.id = ?
                """, (employee_id,))
                value = cursor.fetchone()
                # returns tuple or None if not found
                return value 
            finally:
                cursor.close()
    
    def update_employee_data(self, employee_id, name=None, age=None, sex=None, adress=None, sector_name=None, salary=None):
        with self.lock:
            
            updates = []
            params = []

            if name is not None: updates.append("name = ?"); params.append(name)
            if age is not None: updates.append("age = ?"); params.append(age)
            if sex is not None: updates.append("sex = ?"); params.append(sex)
            if adress is not None: updates.append("adress = ?"); params.append(adress)
            if salary is not None: updates.append("salary = ?"); params.append(salary)
            
            if sector_name is not None:
                sector_id = self._get_or_create_sector_id(sector_name)

                if sector_id is None and sector_name and sector_name.strip(): 
                    print(f"Warning: Could not get or create sector ID for '{sector_name}' during update. Employee sector will not be updated or set to NULL if sector_id is None.")

                updates.append("sector_id = ?")
                params.append(sector_id)

            if not updates:
                return self.search_employee(employee_id)

            sql = f"UPDATE employees SET {', '.join(updates)} WHERE id = ?"
            params.append(employee_id)
            
            cursor = self.connection.cursor()

            try:
                cursor.execute(sql, tuple(params))
                self.connection.commit()
                return self.search_employee(employee_id)
            
            except sqlite3.Error as e:
                print(f"Database error in update_employee_data for ID {employee_id}: {e}")
                self.connection.rollback()
                return None
            
            finally:
                cursor.close()

        
    def delete_employee_data(self, employee_id):
        with self.lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
                deleted_count = cursor.rowcount
                self.connection.commit()
                # True if a row was deleted, False otherwise
                return deleted_count > 0
            except sqlite3.Error as e:
                print(f"Database error in delete_employee_data: {e}")
                self.connection.rollback()
                return False
            finally:
                cursor.close()


    def return_all_employee_data(self):
        with self.lock:
            cursor = self.connection.cursor()
            try:
                # same as search, we need to join tables now
                cursor.execute("""
                    SELECT e.id, e.name, e.age, e.sex, e.adress, s.name as sector_name, e.salary 
                    FROM employees e
                    LEFT JOIN sectors s ON e.sector_id = s.id
                    ORDER BY e.id
                """)
                data = cursor.fetchall()
                # Return list of tuples, or empty list
                return data if data else [] 
            finally:
                cursor.close()

    def add_sector(self, sector_name):
        # here we are returning True for success and False for failures
        if not sector_name or not isinstance(sector_name, str) or sector_name.strip() == "":
            return False
        
        sector_name = sector_name.strip()
        with self.lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute("INSERT INTO sectors (name) VALUES (?)", (sector_name,))
                self.connection.commit()
                return cursor.lastrowid is not None
            
            except sqlite3.IntegrityError:
                return False 
            
            except sqlite3.Error as e:
                print(f"Database error in add_sector: {e}")
                self.connection.rollback()
                return False
            
            finally:
                cursor.close()

    def get_all_sectors(self):
        with self.lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT id, name FROM sectors ORDER BY name")
                return cursor.fetchall()
            finally:
                cursor.close()

    def get_sector_by_id(self, sector_id):
        with self.lock:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT id, name FROM sectors WHERE id = ?", (sector_id,))
                return cursor.fetchone()
            finally:
                cursor.close()
    
    def close_connection(self):
        # closes the database connection
        if self.connection:
            self.connection.close()
            self.connection = None  