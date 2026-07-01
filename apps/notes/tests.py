import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.notes.models import Note


@pytest.fixture
def user(db):
    User = get_user_model()
    user = User.objects.create_user(username="alice", password="hunter2")
    return user


@pytest.fixture
def client(user):
    c = Client()
    c.force_login(user)
    return c


@pytest.mark.django_db
def test_create_note(client, user):
    response = client.post("/notes/new/", {"title": "Hello", "body": "world"})
    assert response.status_code == 200
    assert Note.objects.filter(owner=user, title="Hello").exists()


@pytest.mark.django_db
def test_edit_note(client, user):
    note = Note.objects.create(owner=user, title="Old", body="body")
    response = client.post(f"/notes/{note.pk}/edit/", {"title": "New", "body": "body"})
    assert response.status_code == 200
    note.refresh_from_db()
    assert note.title == "New"


@pytest.mark.django_db
def test_delete_note(client, user):
    note = Note.objects.create(owner=user, title="Doomed", body="")
    response = client.delete(f"/notes/{note.pk}/delete/")
    assert response.status_code == 204
    assert not Note.objects.filter(pk=note.pk).exists()


@pytest.mark.django_db
def test_users_cannot_see_other_notes(client, db):
    User = get_user_model()
    other = User.objects.create_user(username="bob", password="hunter2")
    Note.objects.create(owner=other, title="Bob's secret", body="hidden")
    response = client.get("/")
    assert b"Bob's secret" not in response.content
