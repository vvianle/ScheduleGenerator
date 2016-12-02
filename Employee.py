# represents an employee with name and working day constraints
class Employee(object):

    #initialize an employee with name and day constraints
    def __init__(self, name, constraints):
        #initialize employees, declare a counter to keep track of number of shifts
        self.name = name
        self.constraints = constraints
        self.counter = 0