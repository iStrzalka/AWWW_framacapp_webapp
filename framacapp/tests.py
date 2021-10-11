from django.http import response
from django.test import TestCase
from django.utils.timezone import now

from .models import User, Directory, File, Section
from datetime import datetime
import random
import string

def random_name():
    return ''.join(random.choice(string.ascii_letters) for _ in range(8))


# Create your tests here.
class ModelTests(TestCase):
    def setUp(self):  # Creation tests
        test_case1 = User.objects.create(name="test_case", username="a_username", password="aspdufhl")
        test_case2 = User.objects.create(name="test_case2", username="a_username2", password="aspdufh41l")

        dir1 = Directory.objects.create(name="dir for test_case nr.1", owner=test_case1, creation_date=now())
        dir2 = Directory.objects.create(name="dir for test_case nr.2", owner=test_case2, creation_date=now())

        file = File.objects.create(name="file for test_case nr.1", owner=test_case1, creation_date=now())
        File.objects.create(name="file for test_case nr.2", parent=dir2, owner=test_case2, creation_date=now())

        sec = Section.objects.create(file = file, goal = 'False', description = 'Unable to prove', prover = 'Not Why3', status = 'Failed', data = now())

        super_user = User.objects.create_superuser('admin', 'admin', 'admin')

    def test_can_user1_access_files2(self):
        test_case1 = User.objects.filter(name="test_case")[0]
        self.assertEqual(0, len(File.objects.filter(name="file for test_case nr.2", owner=test_case1)))

    def test_model_str(self):
        test_case4 = User.objects.create(name="test_case4", username="a_username4", password="aspdufhl")
        dir1 = Directory.objects.create(name="this", owner=test_case4, creation_date=now())
        file = File.objects.create(name="<3.c", owner=test_case4, parent=dir1, creation_date=now())
        sec = Section.objects.create(file = file, goal = 'False', description = 'Unable to prove', prover = 'Not Why3', status = 'Failed', data = now())
        self.assertEqual(str(test_case4), 'Username : a_username4')
        self.assertEqual(str(dir1), 'Dir this, Username : a_username4, True')
        self.assertEqual(str(file), 'File <3.c, Username : a_username4, True')
        self.assertEqual(str(sec), 'Section for file <3.c, prover : Not Why3, status : Failed')


from .views import *


class ViewsFunctionalityTests(TestCase):
    def setUp(self):
        test_case1 = User.objects.create(name="test_case1", username="a_username", password="aspdufhl")
        test_case4 = User.objects.create(name="test_case4", username="a_username4", password="aspdufhl")
        dir1 = Directory.objects.create(name="this", owner=test_case4, creation_date=now())
        dir2 = Directory.objects.create(name="test", parent=dir1, owner=test_case4, creation_date=now())
        dir3 = Directory.objects.create(name="was", parent=dir2, owner=test_case4, creation_date=now())
        dir4 = Directory.objects.create(name="passed", parent=dir3, owner=test_case4, creation_date=now())
        file = File.objects.create(name="<3.c", owner=test_case4, parent=dir4, creation_date=now())

    def test_filepath(self):
        file = File.objects.filter(name="<3.c")[0]
        self.assertEqual(get_filepath(file), 'this/test/was/passed/<3.c')

    def test_check_dir(self):
        file = File.objects.filter(name="<3.c")[0]

        test_case4 = User.objects.filter(name="test_case4")[0]
        test_case1 = User.objects.filter(name="test_case1")[0]
        self.assertTrue(check_dir(file.name, True, test_case4))
        self.assertFalse(check_dir(file.name, True, test_case1))
        self.assertTrue(check_dir(file.parent.name, False, test_case4))
        self.assertFalse(check_dir(file.parent.name, False, test_case1))

    def test_program_elements_initially_empty(self):
        file = File.objects.filter(name="<3.c")[0]
        self.assertEqual(get_program_elements(file), '')


class ViewsTests(TestCase):
    def setUp(self):
        test_case1 = User.objects.create_user(name="test_case1", username="a_username", password="aspdufhl")
        test_case4 = User.objects.create_user(name="test_case4", username="a_username4", password="aspdufhl")
        dir1 = Directory.objects.create(name="this", owner=test_case4, creation_date=now())
        dir2 = Directory.objects.create(name="test", parent=dir1, owner=test_case4, creation_date=now())
        dir3 = Directory.objects.create(name="was", parent=dir2, owner=test_case4, creation_date=now())
        dir4 = Directory.objects.create(name="passed", parent=dir3, owner=test_case4, creation_date=now())
        file = File.objects.create(name="right.c", owner=test_case4, parent=dir4, creation_date=now())

    def test_redirects_to_login(self):
        response = self.client.post('')
        self.assertEqual(response.status_code, 302)
        response = self.client.post('', follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/login')

    def test_all_ajax_sites_returns_404(self):
        ajax_sites = ['add_file/', 'add_filep/', 'add_dir/', 'add_dirp/', 'remove/', 'removep/', 'run_prover/',
                      'get_result/', 'load_file/', 'reload_tree/']
        for site in ajax_sites:
            response = self.client.post(site)
            self.assertEqual(response.status_code, 404)

    def test_login_uses_template(self):
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_failed_login(self):
        response = self.client.post('/login/', {'name': 'test_case', 'username': 'username', 'password': 'password'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_accepted_login(self):
        response = self.client.post('/login/', {'name': 'test_case4', 'username': 'a_username4', 'password': 'aspdufhl'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_all_ajax_sites_not_needing_to_interfere(self):
        ajax_sites = ['/add_file/', '/add_dir/', '/remove/', '/run_prover/',
                      '/get_result/', '/load_file/', '/reload_tree/']
        self.client.login(username='a_username4', password='aspdufhl') 
        json_data = {'filename' : 'right.c',}
        for site in ajax_sites:  
            response = self.client.post(site, json_data,
                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
            self.assertEqual(response.status_code, 200)

    def test_all_ajax_procedures(self):
        ajax_sites = ['/add_filep/', '/add_dirp/', '/removep/']
        self.client.login(username='a_username4', password='aspdufhl') 
        
        names = [random_name() + '.c', random_name()]
        with open('./framacapp/for_tests.c') as fp:
            json_data = {'name' : names[0], 'description' : 'test_file',
                'file' : fp, 'id_parent' : 3}
            response = self.client.post('/add_filep/', json_data,
                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
            self.assertEqual(response.status_code, 200)     

        json_data = {'name' : names[1], 'description' : 'test_dir',
                        'id_parent' : 3}
        response = self.client.post('/add_dirp/', json_data,
                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)     

        json_data = {}
        response = self.client.post('/removep/', json_data,
                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)  
        
        json_data = {'isfile' : 'false'}
        response = self.client.post('/removep/', json_data,
                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)  
