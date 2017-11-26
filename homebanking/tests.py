import unittest
import transaction
from pyramid import testing
from .models import (
    Client,
    clientValidation,
    )

class TestClientValidation(unittest.TestCase):
    def test_client_validation(self):
    
        test_cases = (
            (Client(
                login='',
                password='',
                name='',
                first_name='',
                birth_date='',
                address='',
                ), 'Login is mandatory.'),
            (Client(
                login='jdupont',
                password='',
                name='',
                first_name='',
                birth_date='',
                address='',
                ), 'Password is mandatory.'),
            (Client(
                login='jdupont',
                password='password',
                name='',
                first_name='',
                birth_date='',
                address='',
                ), 'Name is mandatory.'),
            (Client(
                login='jdupont',
                password='password',
                name='Dupont',
                first_name='',
                birth_date='',
                address='',
                ), 'First name is mandatory.'),
            (Client(
                login='jdupont',
                password='password',
                name='Dupont',
                first_name='Jacques',
                birth_date='',
                address='',
                ), 'Birth date is mandatory.'),
            (Client(
                login='jdupont',
                password='password',
                name='Dupont',
                first_name='Jacques',
                birth_date='1970-01-01',
                address='',
                ), 'Address is mandatory.'),
            (Client(
                login='jdupont',
                password='password',
                name='Dupont',
                first_name='Jacques',
                birth_date='1970-01-01',
                address='rue de Bruxelles, 20 - 5000 Namur',
                ), ''),
            (Client(
                login='jdupont',
                password='password',
                name='Dupont',
                first_name='Jacques',
                birth_date='azerty',
                address='rue de Bruxelles, 20 - 5000 Namur',
                ), 'Wrong date format.'),
            (Client(
                login='jdupont',
                password='password',
                name='Dupont',
                first_name='Jacques',
                birth_date='1970/01/01',
                address='rue de Bruxelles, 20 - 5000 Namur',
                ), 'Wrong date format.'),
            (Client(
                login='jdupont',
                password='password',
                name='Dupont',
                first_name='Jacques',
                birth_date='1970-01-32',
                address='rue de Bruxelles, 20 - 5000 Namur',
                ), 'Wrong date format.'),
            )
        
        for client, error_msg in test_cases:
            self.assertEquals(clientValidation(client), error_msg, client)