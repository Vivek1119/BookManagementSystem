import sys
import uuid
sys.path.append('../')
import unittest
from httpx import AsyncClient
from app import app
import asyncio

class TestAPI(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = AsyncClient(app=app, base_url="http://127.0.0.1:8000/api/v1/")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_add_book(self):
        response = await self.client.post("/book/", json={
            "id": uuid.uuid4(),
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Test Genre",
            "year_published": 2023,
            "summary": "A test book about AI."
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("summary", response.json())


    async def test_get_all_books(self):
        response = await self.client.get("/books/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


    async def test_get_specific_book(self):
        response = await self.client.get("/books/1")  # Assuming book ID 1 exists
        self.assertIn(response.status_code, [200, 404])  # 200 if exists, 404 if not


    async def test_update_book(self):
        response = await self.client.put("/books/1", json={"title": "Updated Title"})
        self.assertIn(response.status_code, [200, 404])  # 200 if updated, 404 if book not found


    async def test_delete_book(self):
        response = await self.client.delete("/books/1")
        self.assertIn(response.status_code, [200, 404])  # 200 if deleted, 404 if not found


    async def test_add_review(self):
        response = await self.client.post("books/1/reviews/", json={
            "user_id": 1,
            "review_text": "Great book!",
            "rating": 5
        })
        self.assertEqual(response.status_code, 200)


    async def test_get_reviews_for_book(self):
        response = await self.client.get("/reviews/1")
        self.assertIn(response.status_code, [200, 404])


    async def test_get_review_summary(self):
        response = await self.client.get("/reviews/1/summary")
        self.assertIn(response.status_code, [200, 404])  # 200 if reviews exist, 404 if not

if __name__ == "__main__":
    asyncio.run(unittest.main())
