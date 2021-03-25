from werkzeug.security import check_password_hash


class User:

    def __init__(self, username, email, password):
        """
        initialize function for class User
        :param username:
        :param email:
        :param password:
        """
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def is_authenticated():
        """
        checks if a user is logged in or not
        :return: True
        """
        return True

    @staticmethod
    def is_active():
        """
        checks if the user is active or not
        :return: True
        """
        return True

    @staticmethod
    def is_anonymous():
        """
        checks if the user is logged in or just visited the website
        :return: False
        """
        return False

    def get_id(self):
        """
        gets the username for a user
        :return: username
        """
        return self.username

    def check_password(self, password_input):
        """
        checks if the password that is given by the user matches the hashed password available in the database
        :param password_input:
        :return:
        """
        return check_password_hash(self.password, password_input)
