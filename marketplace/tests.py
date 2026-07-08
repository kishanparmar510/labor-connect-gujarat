from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import WorkerProfile, Review

class WorkerProfileModelTest(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='ramesh', password='password123', first_name='Ramesh')
        
        # Create profile
        self.profile = WorkerProfile.objects.create(
            user=self.user,
            name="Ramesh Patel",
            mobile_number="9876543210",
            whatsapp_number="9876543210",
            skill="carpenter",
            experience=7,
            location="vastrapur",
            availability="available",
            daily_rate=600.00,
            bio="Experienced carpenter in Vastrapur area."
        )

    def test_profile_string_representation(self):
        self.assertEqual(str(self.profile), "Ramesh Patel - Carpenter (Suthar)")

    def test_average_rating_no_reviews(self):
        self.assertEqual(self.profile.average_rating, 0.0)
        self.assertEqual(self.profile.review_count, 0)

    def test_average_rating_with_reviews(self):
        # Add reviews
        Review.objects.create(worker=self.profile, customer_name="Amit Shah", rating=5, comment="Excellent work!")
        Review.objects.create(worker=self.profile, customer_name="Sanjay Mehta", rating=4, comment="Very punctual and neat work.")
        
        # Average rating should be 4.5
        self.assertEqual(self.profile.average_rating, 4.5)
        self.assertEqual(self.profile.review_count, 2)


class MarketplaceViewsTest(TestCase):
    def setUp(self):
        # Create users & workers
        self.u1 = User.objects.create_user(username='ramesh', password='password123')
        self.w1 = WorkerProfile.objects.create(
            user=self.u1,
            name="Ramesh Patel",
            mobile_number="9876543210",
            skill="carpenter",
            experience=7,
            location="vastrapur",
            availability="available"
        )
        
        self.u2 = User.objects.create_user(username='hitesh', password='password123')
        self.w2 = WorkerProfile.objects.create(
            user=self.u2,
            name="Hitesh Prajapati",
            mobile_number="8765432109",
            skill="mason",
            experience=10,
            location="satellite",
            availability="busy"
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Labor Connect")
        self.assertContains(response, "Ramesh Patel")
        self.assertContains(response, "Hitesh Prajapati")

    def test_home_page_skill_filter(self):
        # Filter for mason
        response = self.client.get(reverse('home'), {'skill': 'mason'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hitesh Prajapati")
        self.assertNotContains(response, "Ramesh Patel")

    def test_home_page_location_filter(self):
        # Filter for Vastrapur
        response = self.client.get(reverse('home'), {'location': 'vastrapur'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ramesh Patel")
        self.assertNotContains(response, "Hitesh Prajapati")

    def test_home_page_availability_filter(self):
        # Filter for Busy
        response = self.client.get(reverse('home'), {'availability': 'busy'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hitesh Prajapati")
        self.assertNotContains(response, "Ramesh Patel")
