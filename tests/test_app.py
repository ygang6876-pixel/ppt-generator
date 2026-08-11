from io import BytesIO

from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_preview_from_text():
    client = app.test_client()
    response = client.post(
        "/api/preview",
        data={"content_text": "# Demo\n\n## Slide\n\n- One\n- Two"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Demo"
    assert data["total_pages"] >= 1


def test_generate_from_uploaded_markdown():
    client = app.test_client()
    response = client.post(
        "/api/generate",
        data={
            "content_file": (BytesIO(b"# Demo\n\n## Slide\n\n- One"), "demo.md"),
            "theme": "clean",
            "output_name": "demo",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert response.data[:2] == b"PK"
