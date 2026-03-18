from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_routes():
    print("Testing GET /api/products")
    response = client.get("/api/products")
    print(f"Status: {response.status_code}")
    print(f"Data: {response.json()}")
    assert response.status_code == 200
    assert "data" in response.json()
    assert "success" in response.json()
    
    print("\nAPI Architecture Test Passed!")

if __name__ == "__main__":
    test_routes()
