from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Pydantic Models
class Book(BaseModel):
    id: int
    title: str
    author_id: int
    price: float
    stock: int

class Author(BaseModel):
    id: int
    name: str
    bio: Optional[str] = None

class Order(BaseModel):
    id: int
    book_id: int
    quantity: int
    total_price: float
    status: str  # e.g., "completed", "pending", "canceled"

# In-memory storage
books = [
    Book(id=1, title="1984", author_id=1, price=15.99, stock=100),
    Book(id=2, title="To Kill a Mockingbird", author_id=2, price=10.99, stock=50),
]
authors = [
    Author(id=1, name="George Orwell", bio="British novelist and essayist."),
    Author(id=2, name="Harper Lee", bio="American novelist best known for 'To Kill a Mockingbird'."),
]
orders = []

# Helper Functions
def find_item_by_id(items, item_id):
    return next((item for item in items if item.id == item_id), None)

# Endpoints for Books

@app.get("/books", response_model=List[Book])
def get_books(author_id: Optional[int] = None, price_min: Optional[float] = None, price_max: Optional[float] = None, sort_by: Optional[str] = None, page: int = 1, limit: int = 10):
    filtered_books = books
    
    # Filter by author
    if author_id:
        filtered_books = [book for book in filtered_books if book.author_id == author_id]
    
    # Filter by price range
    if price_min is not None:
        filtered_books = [book for book in filtered_books if book.price >= price_min]
    if price_max is not None:
        filtered_books = [book for book in filtered_books if book.price <= price_max]
    
    # Sorting
    if sort_by == "price_asc":
        filtered_books.sort(key=lambda x: x.price)
    elif sort_by == "price_desc":
        filtered_books.sort(key=lambda x: x.price, reverse=True)
    
    # Pagination
    start = (page - 1) * limit
    end = start + limit
    return filtered_books[start:end]

@app.get("/books/{id}", response_model=Book)
def get_book(id: int):
    book = find_item_by_id(books, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=Book, status_code=201)
def create_book(book: Book):
    if find_item_by_id(books, book.id):
        raise HTTPException(status_code=400, detail="Book with this ID already exists")
    books.append(book)
    return book

@app.put("/books/{id}", response_model=Book)
def update_book(id: int, updated_book: Book):
    book = find_item_by_id(books, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.title = updated_book.title
    book.author_id = updated_book.author_id
    book.price = updated_book.price
    book.stock = updated_book.stock
    return book

@app.delete("/books/{id}", status_code=204)
def delete_book(id: int):
    global books
    books = [book for book in books if book.id != id]
    return None

# Endpoints for Authors

@app.get("/authors", response_model=List[Author])
def get_authors():
    return authors

@app.get("/authors/{id}", response_model=Author)
def get_author(id: int):
    author = find_item_by_id(authors, id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@app.post("/authors", response_model=Author, status_code=201)
def create_author(author: Author):
    if find_item_by_id(authors, author.id):
        raise HTTPException(status_code=400, detail="Author with this ID already exists")
    authors.append(author)
    return author

@app.put("/authors/{id}", response_model=Author)
def update_author(id: int, updated_author: Author):
    author = find_item_by_id(authors, id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    author.name = updated_author.name
    author.bio = updated_author.bio
    return author

@app.delete("/authors/{id}", status_code=204)
def delete_author(id: int):
    global authors
    authors = [author for author in authors if author.id != id]
    return None

# Endpoints for Orders
@app.post("/orders", response_model=Order, status_code=201)
def create_order(order: Order):
    book = find_item_by_id(books, order.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    book.stock -= order.quantity
    order.total_price = order.quantity * book.price
    orders.append(order)
    return order

@app.get("/orders", response_model=List[Order])
def get_orders():
    return orders

@app.get("/orders/{id}", response_model=Order)
def get_order(id: int):
    order = find_item_by_id(orders, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
