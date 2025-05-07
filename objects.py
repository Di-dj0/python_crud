class CRUD_object:

    def __init__(self, name, age, sex, adress, sector, salary, id=None):
        self.id = id
        self.name = name
        self.age = age
        self.sex = sex
        self.adress = adress
        self.sector = sector
        self.salary = salary


def convert_to_dict(object:CRUD_object) -> dict:
    return {
        '__class__': 'objects.CRUD_object',
        'id': object.id,
        'name': object.name,
        'age': object.age,
        'sex': object.sex,
        'adress': object.adress,
        'sector': object.sector,
        'salary': object.salary
    }


def convert_to_object(classname, dictionary: dict):
    employee = CRUD_object(dictionary['name'], dictionary['age'],dictionary['sex'],dictionary['adress'],dictionary['sector'],dictionary['salary'],dictionary['id'])
    return employee