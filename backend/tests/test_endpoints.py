from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


# check if SwaggerUI is up and running (for FastAPI)
def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200


# calling root
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Use the RESTful API"}  # exact JSON
    payload = response.json()
    assert "RESTful" in payload["message"]                        # a keyword

# ----- CRUD operations: test sequence RCUD ----- #


def random_string(length=8):
    import uuid
    return "deleteMe_"+str(uuid.uuid4())[:length]


number_of_items = 0
test_id = 0
test_payload = {"name": random_string(), "description": "This is a test item"}


def test_read_items():
    response = client.get("/items")
    assert response.status_code == 200
    global number_of_items
    number_of_items = len(response.json())


def test_create_item():
    # Create item
    response = client.post("/items", json=test_payload)
    assert response.status_code == 200
    #
    # Check response
    data = response.json()
    assert data["name"] == test_payload["name"]
    assert data["description"] == test_payload["description"]
    assert "id" in data
    global test_id
    test_id = data["id"]
    #
    # Was it successfully committed to the database?
    response = client.get("/items")
    assert len(response.json()) == number_of_items + 1


def test_update_item():
    # new payload
    test_payload["description"] = random_string()
    response = client.put(f"/items/{test_id}", json=test_payload)
    assert response.status_code == 200
    #
    # Retrieve & check the updated record
    response = client.get(f"/items/{test_id}")
    data = response.json()
    assert data["name"] == test_payload["name"]
    assert data["description"] == test_payload["description"]


def test_search(keyword="deleteMe_"):
    response = client.get(f"/search/{keyword}?limit=10")
    assert response.status_code == 200
    #
    # Validate the IDs
    data = response.json()
    list_ids = [(k["id"] > 0) for k in data]
    assert False not in list_ids        # must be valid IDs


def test_delete_item():
    response = client.delete(f"/items/{test_id}")
    assert response.status_code == 200
    #
    # Was it successfully deleted from the database?
    response = client.get("/items")
    assert len(response.json()) == number_of_items
