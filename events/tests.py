from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from .models import Event, Reservation
from threading import Thread

User = get_user_model()


class TestEventAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alice", password="pass123")

    def test_signup_and_login(self):
        # signup
        signup_client = APIClient()
        response = signup_client.post("/api/signup/", {
            "username": "bob",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)

        # login
        login_client = APIClient()
        response = login_client.post("/api/login/", {
            "username": "bob",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_event_creation(self):
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        data = {
            "title": "Test Event",
            "description": "Event Description",
            "category": "workshop",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "capacity": 5
        }
        token = self.client.post("/api/login/", {
            "username": "alice",
            "password": "pass123"
        }).data["token"]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.post("/api/events/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 1)

    def test_reservation_creation(self):
        event = Event.objects.create(
            title="Test Event",
            description="Event Desc",
            category="sports",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            capacity=2,
            creator=self.user
        )
        token = self.client.post("/api/login/", {
            "username": "alice",
            "password": "pass123"
        }).data["token"]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.post(f"/api/events/{event.id}/reserve/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_duplicate_reservation_prevention(self):
        event = Event.objects.create(
            title="Duplicate Test Event",
            description="Event Desc",
            category="sports",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            capacity=2,
            creator=self.user
        )
        token = self.client.post("/api/login/", {
            "username": "alice",
            "password": "pass123"
        }).data["token"]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        r1 = self.client.post(f"/api/events/{event.id}/reserve/")
        r2 = self.client.post(f"/api/events/{event.id}/reserve/")
        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r2.status_code, 400)
        self.assertIn("already reserved", str(r2.data).lower())


class TestReservationConcurrency(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.u1 = User.objects.create_user("u1", password="pwd1")
        self.u2 = User.objects.create_user("u2", password="pwd2")
        self.event = Event.objects.create(
            title="Race Event",
            description="Test Desc",
            category="sports",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            capacity=1,
            creator=self.u1
        )

    def try_reserve(self, username, password, results, idx):
        client = APIClient()
        token = client.post("/api/login/", {
            "username": username,
            "password": password
        }).data["token"]
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        resp = client.post(f"/api/events/{self.event.id}/reserve/")
        results[idx] = resp.status_code

    def test_no_overbooking(self):
        results = {}
        t1 = Thread(target=self.try_reserve, args=("u1", "pwd1", results, 1))
        t2 = Thread(target=self.try_reserve, args=("u2", "pwd2", results, 2))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        success_count = sum(1 for code in results.values() if code == 201)
        self.assertEqual(success_count, 1, "Only one reservation should succeed")
