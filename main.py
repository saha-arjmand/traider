
class Employee:

    raise_amount = 1.04

    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.pay = pay
        self.email = first + '.' + last + '@company.com'

    def fullname(self):
        return '{} {}'.format(self.first, self.last)

    def apply_raise(self):
        self.pay = int(self.pay * Employee.raise_amount)


emp_1 = Employee('Amir', 'Arjmand', 50000)
emp_2 = Employee('User', 'Test', 60000)

print(emp_1.raise_amount)
print(emp_2.raise_amount)
print(Employee.raise_amount)
print()

emp_1.raise_amount = 1.05

print(emp_1.raise_amount)
print(emp_2.raise_amount)
print(Employee.raise_amount)

# end
