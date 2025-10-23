from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from myapp.models import User

class UserAPITests(APITestCase):
    def setUp(self):
        
        self.user = User.objects.create(
            name="kalyan",
            email="kalyan@example.com",
            Batch=22,
            weight=60
        )
        self.list_url = reverse('user-list')   
        self.detail_url = reverse('user-detail', args=[self.user.id])  

    def test_get_user_list(self):
        """Test retrieving all users (GET /users/)"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn('name', response.data[0])

    def test_create_user(self):
        """Test creating a new user (POST /users/)"""
        data = {
            "name": "Sachin",
            "email": "Sachin@example.com",
            "Batch": 20,
            "weight": 70
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(id=response.data['id']).name, "Sachin")

    def test_get_user_detail(self):
        """Test retrieving a single user (GET /users/{id}/)"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.user.name)

    def test_update_user(self):
        """Test updating a user (PUT /users/{id}/)"""
        data = {
            "name": "kalyan Updated",
            "email": "kalyan@example.com",
            "Batch": 20,
            "weight": 62
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "kalyan Updated")
        self.assertEqual(self.user.Batch, 20)

    def test_delete_user(self):
        """Test deleting a user (DELETE /users/{id}/)"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_unique_email_constraint(self):
        """Test that creating a user with an existing email fails"""
        data = {
            "name": "Duplicate Email",
            "email": "kalyan@example.com", 
            "Batch": 25,
            "weight": 55
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["errors"])