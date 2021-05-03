from django.test import TestCase
from django.utils.timezone import now

from .models import User, Directory, File
from datetime import datetime


# Create your tests here.
class ModelTests(TestCase):
    def setUp(self):  # Creation tests
        test_case1 = User.objects.create(name="test_case", username="a_username", password="aspdufhl")
        test_case2 = User.objects.create(name="test_case2", username="a_username2", password="aspdufh41l")

        dir1 = Directory.objects.create(name="dir for test_case nr.1", owner=test_case1, creation_date=now())
        dir2 = Directory.objects.create(name="dir for test_case nr.2", owner=test_case2, creation_date=now())

        File.objects.create(name="file for test_case nr.1", owner=test_case1, creation_date=now())
        File.objects.create(name="file for test_case nr.2", parent=dir2, owner=test_case2, creation_date=now())

    def test_can_user1_access_files2(self):
        test_case1 = User.objects.filter(name="test_case")[0]
        self.assertEqual(0, len(File.objects.filter(name="file for test_case nr.2", owner=test_case1)))

    def test_model_str(self):
        test_case4 = User.objects.create(name="test_case4", username="a_username4", password="aspdufhl")
        dir1 = Directory.objects.create(name="this", owner=test_case4, creation_date=now())
        file = File.objects.create(name="<3.c", owner=test_case4, parent=dir1, creation_date=now())
        self.assertEqual(str(test_case4), 'Username : a_username4')
        self.assertEqual(str(dir1), 'Dir this, Username : a_username4, True')
        self.assertEqual(str(file), 'File <3.c, Username : a_username4, True')


from .views import get_filepath, check_dir, get_program_elements


class ViewTests(TestCase):
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
