from django.test import RequestFactory, TestCase
from django.urls import reverse
from main.models import myUser, department, course
from django.db import IntegrityError
from .views import editprofile

# Create your tests here.
class URLTest(TestCase):
    def test_main_page_url(self):
        response = self.client.get('/main/')
        self.assertTrue(response.status_code == 200)

    def test_fake_url(self):
        response = self.client.get('/fake/')
        self.assertFalse(response.status_code == 200)

    def test_course_catalog_url(self):
        response = self.client.get('/main/coursecatalog/')
        self.assertTrue(response.status_code == 200)

    def test_search_class_url(self):
        response = self.client.get('/main/searchclass/')
        self.assertTrue(response.status_code == 200)

    def test_my_schedule_url(self):
        response = self.client.get('/main/myschedule/')
        self.assertTrue(response.status_code == 200)

class UserTestCase(TestCase):
    def setUp(self, id=0, name="", email="", summary="", major="", graduationYear=0):
        self.factory = RequestFactory()
        return myUser.objects.create(id = id,name=name,email=email,summary=summary,major=major,graduationYear=graduationYear)

    def test_user_creation(self):
        user = self.setUp(id = 1,name="FirstLast",email="FL1@gmailcom",summary="sum",major="CS",graduationYear=2024)
        self.assertTrue(isinstance(user,myUser))
        self.assertEqual(user.__str__(), user.name)

    def test_invalid_user(self):
        failed = False
        try:
            bad= myUser.objects.create()
        except:
            failed = True
        self.assertTrue(failed)

class DepartmentTestCase(TestCase):
    def setUp(self, abbreviation="abv", departmentName="CS"):
        return department.objects.create(abbreviation=abbreviation,departmentName=departmentName)

    def test_department_creation(self):
        dep = self.setUp()
        self.assertTrue(isinstance(dep, department))
        self.assertEqual(dep.__str__(),dep.abbreviation)

    def test_department_name(self):
        dep=self.setUp()
        self.assertEqual(dep.departmentName, "CS")
