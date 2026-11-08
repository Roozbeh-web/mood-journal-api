from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from entries.models import Entry

User = get_user_model()

class EntryAPITests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='alice', password='pass12345')
        self.user_b = User.objects.create_user(username='bob', password='pass12345')
        self.token_a = Token.objects.create(user=self.user_a)
        self.token_b = Token.objects.create(user=self.user_b)

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get('/api/entries/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_entry_computes_mood_score(self):
        self._auth(self.token_a)
        response = self.client.post('/api/entries/', {'text': 'امروز خیلی خوب و عالی بود'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(response.data['mood_score'], 0)
        self.assertEqual(Entry.objects.count(), 1)
        self.assertEqual(Entry.objects.first().user, self.user_a)

    def test_client_cannot_forge_mood_score(self):
        self._auth(self.token_a)
        response = self.client.post(
            '/api/entries/',
            {'text': 'خیلی خسته و ناراحت بودم', 'mood_score': 1.0}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertLess(response.data['mood_score'], 0)

    def test_client_cannot_set_owner(self):
        self._auth(self.token_a)
        response = self.client.post(
            '/api/entries/',
            {'text': 'تست', 'user': self.user_b.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        entry = Entry.objects.first()
        self.assertEqual(entry.user, self.user_a)

    def test_list_returns_only_own_entries(self):
        Entry.objects.create(user=self.user_a, text='الف', mood_score=0.5)
        Entry.objects.create(user=self.user_b, text='ب', mood_score=0.5)

        self._auth(self.token_a)
        response = self.client.get('/api/entries/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'الف')

    def test_user_cannot_retrieve_other_users_entry(self):
        entry_b = Entry.objects.create(user=self.user_b, text='خصوصی', mood_score=-0.5)

        self._auth(self.token_a)
        response = self.client.get(f'/api/entries/{entry_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_other_users_entry(self):
        entry_b = Entry.objects.create(user=self.user_b, text='محفوظ', mood_score=0.0)

        self._auth(self.token_a)
        response = self.client.delete(f'/api/entries/{entry_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Entry.objects.filter(id=entry_b.id).exists())

    def test_update_recomputes_mood_score(self):
        entry = Entry.objects.create(user=self.user_a, text='خوب', mood_score=1.0)

        self._auth(self.token_a)
        response = self.client.patch(f'/api/entries/{entry.id}/', {'text': 'خیلی ناراحت و عمگین بودم'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        self.assertLess(entry.mood_score, 0)

class EntryStatsAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ali', password='pass12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_stats_requires_auth(self):
        self.client.credentials()
        response = self.client.get('/api/entries/stats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_empty(self):
        response = self.client.get('/api/entries/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_entries'], 0)
        self .assertIsNone(response.data['average_mood'])

    def test_stats_count_by_sentiment(self):
        Entry.objects.create(user=self.user, text='a', mood_score=0.8)
        Entry.objects.create(user=self.user, text='b', mood_score=0.5)
        Entry.objects.create(user=self.user, text='c', mood_score=-0.7)
        Entry.objects.create(user=self.user, text='d', mood_score=0.0)

        response = self.client.get('/api/entries/stats/')
        self.assertEqual(response.data['total_entries'], 4)
        self.assertEqual(response.data['positive_entries'], 2)
        self.assertEqual(response.data['negative_entries'], 1)
        self.assertEqual(response.data['neutral_entries'], 1)

    def test_stats_only_include_own_entries(self):
        other = User.objects.create_user(username='mamad', password='pass12345')
        Entry.objects.create(user=self.user, text='mine', mood_score=0.5)
        Entry.objects.create(user=other, text='theirs', mood_score=0.9)

        response = self.client.get('/api/entries/stats/')
        self.assertEqual(response.data['total_entries'], 1)