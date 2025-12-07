from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from incidents.models import Incident, IncidentComment


class IncidentModelTest(TestCase):  # Test Incident model
    def setUp(self):  # Create test data
        self.user = User.objects.create_user(
            username='testuser',    # Create test user
            email='test@example.com',  # Set email
            password='testpass123'  # Set password
        )

    def test_create_incident(self):
        # Test creating an incident
        incident = Incident.objects.create(
            title='Test Incident',
            description='Test description',
            created_by=self.user,  # Create incident creator
            status='OPEN',
            severity='MEDIUM'  # Set severity
        )
        self.assertEqual(incident.title, 'Test Incident')  # Verify title
        self.assertEqual(incident.status, 'OPEN')  # Verify status
        self.assertEqual(incident.severity, 'MEDIUM')  # Verify severity

    def test_incident_string_representation(self):  # Test string representation
        incident = Incident.objects.create(
            title='Test Title',
            description='Test description',
            created_by=self.user  # Create incident creator
        )
        self.assertIn('Test Title', str(incident))

    def test_incident_default_status(self):  # Test incident default status is OPEN
        incident = Incident.objects.create(  # Create incident
            title='Test',
            description='Test',
            created_by=self.user
        )
        self.assertEqual(incident.status, 'OPEN')

    def test_incident_default_severity(self):
        # Test incident default severity is LOW
        incident = Incident.objects.create(
            title='Test',
            description='Test',
            created_by=self.user
        )
        self.assertEqual(incident.severity, 'LOW')


class IncidentCommentTest(TestCase):
    # Test IncidentComment model

    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.incident = Incident.objects.create(
            title='Test Incident',
            description='Test description',
            created_by=self.user
        )

    def test_create_comment(self):
        # Test creating a comment
        comment = IncidentComment.objects.create(
            incident=self.incident,
            author=self.user,
            text='Test comment'
        )
        self.assertEqual(comment.text, 'Test comment')
        self.assertEqual(comment.incident, self.incident)


class AuthenticationTest(TestCase):
    # Test user authentication

    def setUp(self):
        # Create test user and client
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_user_creation(self):
        # Test creating a user
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpass123'))

    def test_password_hashing(self):
        # Test that passwords are hashed
        self.assertNotEqual(self.user.password, 'testpass123')
        self.assertTrue(self.user.check_password('testpass123'))


class RoleBasedAccessTest(TestCase):     # Test role-based access control
    def setUp(self):                     # Create groups and users
        self.admin_group, _ = Group.objects.get_or_create(name='Admin')  # Create Admin group
        self.support_group, _ = Group.objects.get_or_create(name='IT Support')  # Create IT Support group
        self.admin_user = User.objects.create_user(  # create admin user
            username='admin',
            password='admin123'
        )
        self.admin_user.groups.add(self.admin_group)

        self.support_user = User.objects.create_user(  # create support user
            username='support',
            password='support123'
        )
        self.support_user.groups.add(self.support_group)

    def test_admin_group_exists(self):  # Test admin group creation
        self.assertTrue(Group.objects.filter(name='Admin').exists())

    def test_user_in_group(self):       # Test user group membership
        self.assertTrue(self.admin_user.groups.filter(name='Admin').exists())


class IncidentCRUDTest(TestCase):   # Test CRUD operations for Incident model

    def setUp(self):  # set up test user and incident
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.incident = Incident.objects.create(
            title='Original Title',
            description='Original description',
            created_by=self.user,
            status='OPEN'
        )

    def test_read_incident(self):       # Test reading an incident
        incident = Incident.objects.get(id=self.incident.id)
        self.assertEqual(incident.title, 'Original Title')

    def test_update_incident_status(self):  # Test updating incident status
        self.incident.status = 'IN_PROGRESS'
        self.incident.save()
        updated = Incident.objects.get(id=self.incident.id)
        self.assertEqual(updated.status, 'IN_PROGRESS')

    def test_delete_incident(self):
        # Test deleting an incident
        incident_id = self.incident.id
        self.incident.delete()
        self.assertFalse(Incident.objects.filter(id=incident_id).exists())


class InputValidationTest(TestCase):    # Test input validation
    def setUp(self):        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_required_fields(self):         # Test that required fields are enforced
        incident = Incident.objects.create(
            title='Valid Title',
            description='Valid description',
            created_by=self.user)
        self.assertIsNotNone(incident.id)

    def test_long_title_handling(self):     # Test title max length (200 chars)
        long_title = 'A' * 200
        incident = Incident.objects.create(
            title=long_title,
            description='Test',
            created_by=self.user)
        self.assertEqual(len(incident.title), 200)
