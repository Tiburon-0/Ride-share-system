class User:

    '''Initializes User Parent class'''

    def __init__(self, name, user_id):
        self._name = name
        self._user_id = user_id
        self._ratings = []

    def __str__(self):
        '''User-friendly display for User'''
        average_rating = self.get_average_rating()
        return f"{self._name}, User ID: {self._user_id}, Rating: {average_rating}"

    # Getter methods

    def get_name(self):
        '''Get user's name'''
        return self._name

    def get_user_id(self):
        '''Get user's id'''
        return self._user_id

    def get_ratings(self):
        '''Get list of all ratings'''
        return self._ratings

    def get_average_rating(self):
        '''Calculates average rating'''
        if len(self._ratings) == 0:
            return 0.0
        else:
            return sum(self._ratings) / len(self._ratings)

    # Setter methods

    def set_name(self, name):
        '''Updates user's name'''
        self._name = name
        return self._name

    # Rating methods

    def add_rating(self, rating):
        '''Adds rating to a user'''
        if rating >= 1 and rating <= 5:
            self._ratings.append(rating)
            return self._ratings
        else:
            print(
                "Invalid rating input: {rating}. Rating must be between 1 and 5.")
            return None
