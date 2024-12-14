# Library Management System API

This project is a Flask-based RESTful API for a Library Management System. It supports user registration, book management, borrow requests, and book returns. Authentication is implemented using Basic Auth, and data is stored in an SQLite database.

---

## Features

- **User Registration**: Users can register as members or librarians.
- **Book Management**: Librarians can add books to the library.
- **Borrow Requests**: Users can request books for specific dates.
- **Return Books**: Librarians can mark books as returned.
- **User Borrow History**: Users can view their borrow history.

---

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/omkarbhusnale/library-management-api.git
   cd library-management-api
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python app.py
   ```

The API will be accessible at `http://127.0.0.1:5000/`.

---

## API Endpoints

### User Registration

- **URL**: `/register`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "is_librarian": true
  }
  ```
- **Response**:
  - **Success**: `201 Created`
    ```json
    {
      "message": "User created successfully."
    }
    ```
  - **Failure**: `400 Bad Request`
    ```json
    {
      "message": "User with this email already exists."
    }
    ```

---

### Get All Books

- **URL**: `/getBooks`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Basic <base64-encoded-email-password>`
- **Response**:
  ```json
  [
    {
      "id": 1,
      "title": "Book Title",
      "author": "Author Name",
      "available": true
    }
  ]
  ```

---

### Add a Book

- **URL**: `/addBook`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Basic <base64-encoded-email-password>`
- **Request Body**:
  ```json
  {
    "title": "New Book",
    "author": "Author Name"
  }
  ```
- **Response**:
  - **Success**: `201 Created`
    ```json
    {
      "message": "Book added successfully."
    }
    ```
  - **Failure**: `403 Forbidden`
    ```json
    {
      "message": "Only librarians can add books."
    }
    ```

---

### Request a Book

- **URL**: `/requestBook`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Basic <base64-encoded-email-password>`
- **Request Body**:
  ```json
  {
    "book_id": 1,
    "start_date": "2024-12-01",
    "end_date": "2024-12-10"
  }
  ```
- **Response**:
  - **Success**: `201 Created`
    ```json
    {
      "message": "Borrow request submitted successfully."
    }
    ```
  - **Failure**: `400 Bad Request`
    ```json
    {
      "message": "Book is not available for the requested period."
    }
    ```

---

### Mark Book as Returned

- **URL**: `/requests/<request_id>/return`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Basic <base64-encoded-email-password>`
- **Response**:
  - **Success**: `200 OK`
    ```json
    {
      "message": "Book marked as returned successfully."
    }
    ```
  - **Failure**: `403 Forbidden`
    ```json
    {
      "message": "Only librarians can mark books as returned."
    }
    ```

---

### User Borrow History

- **URL**: `/user/borrow_history`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Basic <base64-encoded-email-password>`
- **Response**:
  ```json
  [
    {
      "book_id": 1,
      "start_date": "2024-12-01",
      "end_date": "2024-12-10",
      "status": "Approved"
    }
  ]
  ```

---

## Database Models

### User

- `id`: Integer, Primary Key
- `email`: String (unique, required)
- `password`: String (hashed)
- `is_librarian`: Boolean (default: False)

### Book

- `id`: Integer, Primary Key
- `title`: String (required)
- `author`: String (required)
- `available`: Boolean (default: True)

### BorrowRequest

- `id`: Integer, Primary Key
- `user_id`: Foreign Key (User)
- `book_id`: Foreign Key (Book)
- `start_date`: Date
- `end_date`: Date
- `status`: String (default: Pending)

---

## Testing the API with Postman

1. Open Postman.
2. Import a new collection and set the following details:
   - **Base URL**: `http://127.0.0.1:5000`
   - Use the endpoints and request bodies provided in this documentation.
3. Set **Authorization** to `Basic Auth` for protected routes, and provide the email and password.
4. Test each endpoint to verify functionality.

---

## Requirements

- Flask
- Flask-SQLAlchemy
- Flask-HTTPAuth
- Flask-JWT-Extended

---

## Notes

- Ensure the database is created by running the app at least once.
- Modify `app.config['SQLALCHEMY_DATABASE_URI']` to use a different database if needed.
- You can find out Postman API Request Handling Json inside `LibraryManagment.postman_collection.json` file.

---

## Future Improvements

- Add JWT-based token authentication.
- Implement pagination for large book collections.
- Add admin dashboards and user interfaces.
- Integrate email notifications for borrow requests.

---

## License

MIT License
