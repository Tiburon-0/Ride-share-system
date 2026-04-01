class Car:

    '''Intializes car class'''

    def __init__(self, year, make, model, plate_number):
        self._year = year
        self._make = make
        self._model = model
        self._plate_number = plate_number

    def __str__(self):
        '''User-friendly display for Car object'''
        return f"Year: {self._year} Make: {self._make} Model: {self._model} Plate: {self._plate_number}"

    # Getter methods

    def get_year(self):
        '''Returns year of car model'''
        return self._year

    def get_make(self):
        '''Returns car make'''
        return self._make

    def get_model(self):
        '''Returns car model'''
        return self._model

    def get_plate_number(self):
        '''Returns car plate number'''
        return self._plate_number

    # Behavior methods

    def get_description(self):
        '''Returns car description'''
        return f"This car is a {self._year} {self._make} {self._model}. License plate: {self._plate_number}."


class SelfDrivenCar(Car):
    '''Creates SelfDrivenCar subclass'''

    def get_description(self):
        '''Returns description for SelfDrivenCar subclass'''
        self_driven_car_description = super().get_description()
        return f"Self-driven car description: {self_driven_car_description}"


class HumanDrivenCar(Car):
    '''Creates HumanDrivenCar subclass'''

    def get_description(self):
        '''Returns description for SelfDrivenCar subclass'''
        human_driven_car_description = super().get_description()
        return f" Human-driven car description: {human_driven_car_description}"







