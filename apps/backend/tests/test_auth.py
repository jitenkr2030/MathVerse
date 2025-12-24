"""
MathVerse Backend API - Authentication Tests
==============================================
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """
    Test user registration.
    """
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User",
            "role": "student"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate_email(client: TestClient, test_user: dict):
    """
    Test registration with duplicate email.
    """
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "anotheruser",
            "password": "SecurePass123!",
            "full_name": "Another User"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client: TestClient, test_user: User):
    """
    Test successful login.
    """
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user: User):
    """
    Test login with wrong password.
    """
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_get_current_user(auth_headers: dict, client: TestClient):
    """
    Test getting current user info.
    """
    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_current_user_unauthorized(client: TestClient):
    """
    Test getting current user without auth.
    """
    response = client.get("/api/auth/me")
    
    assert response.status_code == 403


def test_refresh_token(client: TestClient, test_user: User):
    """
    Test token refresh.
    """
    # First login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_logout(auth_headers: dict, client: TestClient):
    """
    Test logout endpoint.
    """
    response = client.post("/api/auth/logout", headers=auth_headers)
    
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]
