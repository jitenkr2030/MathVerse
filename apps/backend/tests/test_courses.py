"""
MathVerse Backend API - Courses Tests
======================================
Tests for course management endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_list_courses(client: TestClient):
    """
    Test listing courses.
    """
    response = client.get("/api/courses/")
    
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    assert "total" in data
    assert "page" in data


def test_create_course_unauthorized(client: TestClient):
    """
    Test creating course without authentication.
    """
    response = client.post(
        "/api/courses/",
        json={
            "title": "Test Course",
            "description": "Test description",
            "level": "secondary",
            "subject": "Algebra"
        }
    )
    
    assert response.status_code == 403


def test_create_course_as_student(auth_headers: dict, client: TestClient):
    """
    Test creating course as student (should fail).
    """
    response = client.post(
        "/api/courses/",
        json={
            "title": "Test Course",
            "description": "Test description",
            "level": "secondary",
            "subject": "Algebra"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 403


def test_create_course_as_creator(creator_auth_headers: dict, client: TestClient):
    """
    Test creating course as creator.
    """
    response = client.post(
        "/api/courses/",
        json={
            "title": "Algebra Basics",
            "description": "Learn the fundamentals of algebra",
            "level": "secondary",
            "subject": "Algebra",
            "price": 19.99,
            "is_free": False
        },
        headers=creator_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Algebra Basics"
    assert data["level"] == "secondary"
    assert data["is_published"] == False


def test_get_course(client: TestClient, creator_auth_headers: dict):
    """
    Test getting course details.
    """
    # First create a course
    create_response = client.post(
        "/api/courses/",
        json={
            "title": "Geometry Fundamentals",
            "description": "Learn geometry basics",
            "level": "secondary",
            "subject": "Geometry"
        },
        headers=creator_auth_headers
    )
    course_id = create_response.json()["id"]
    
    # Get the course
    response = client.get(f"/api/courses/{course_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Geometry Fundamentals"


def test_update_course(creator_auth_headers: dict, client: TestClient):
    """
    Test updating course.
    """
    # Create a course
    create_response = client.post(
        "/api/courses/",
        json={
            "title": "Calculus Intro",
            "description": "Introduction to calculus",
            "level": "senior_secondary",
            "subject": "Calculus"
        },
        headers=creator_auth_headers
    )
    course_id = create_response.json()["id"]
    
    # Update the course
    response = client.put(
        f"/api/courses/{course_id}",
        json={
            "title": "Calculus Fundamentals",
            "description": "Master the fundamentals of calculus"
        },
        headers=creator_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Calculus Fundamentals"


def test_delete_course(creator_auth_headers: dict, client: TestClient):
    """
    Test deleting course.
    """
    # Create a course
    create_response = client.post(
        "/api/courses/",
        json={
            "title": "Trigonometry",
            "description": "Learn trigonometry",
            "level": "secondary",
            "subject": "Trigonometry"
        },
        headers=creator_auth_headers
    )
    course_id = create_response.json()["id"]
    
    # Delete the course
    response = client.delete(
        f"/api/courses/{course_id}",
        headers=creator_auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify deleted
    get_response = client.get(f"/api/courses/{course_id}")
    assert get_response.status_code == 404


def test_filter_courses_by_level(client: TestClient):
    """
    Test filtering courses by level.
    """
    response = client.get("/api/courses/?level=secondary")
    
    assert response.status_code == 200
    data = response.json()
    for course in data["courses"]:
        assert course["level"] == "secondary"


def test_filter_courses_by_subject(client: TestClient):
    """
    Test filtering courses by subject.
    """
    response = client.get("/api/courses/?subject=Algebra")
    
    assert response.status_code == 200
    data = response.json()
    for course in data["courses"]:
        assert course["subject"] == "Algebra"
