from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from models import db, User, Book, BorrowRequest
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

auth = HTTPBasicAuth()

db.init_app(app)

with app.app_context():
    db.create_all()

from models import User, Book, BorrowRequest

# Authentication function
@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    is_librarian = data.get('is_librarian', False)

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    existing_User = User.query.filter(User.email.ilike(email)).first()
    if existing_User:
        return jsonify({"message": "User with this email already exists."}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, is_librarian=is_librarian)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully."}), 201

@app.route('/getBooks', methods=['GET'])
@auth.login_required
def get_books():
    books = Book.query.all()
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "available": book.available
    } for book in books])

@app.route('/addBook', methods=['POST'])
@auth.login_required
def add_book():
    user = auth.current_user()
    if not user.is_librarian:
        return jsonify({"message": "Only librarians can add books."}), 403

    data = request.json
    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({"message": "Both title and author are required."}), 400

    # Check if the book title already exists
    existing_book = Book.query.filter(Book.title.ilike(title)).first()
    if existing_book:
        return jsonify({"message": "Book with this title already exists."}), 400

    # Add the new book
    new_book = Book(title=title, author=author, available=True)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully."}), 201

@app.route('/requestBook', methods=['POST'])
@auth.login_required
def request_book():
    user = auth.current_user()
    data = request.json
    book_id = data.get('book_id')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not book_id or not start_date_str or not end_date_str:
        return jsonify({"message": "All fields are required."}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Check if the book is available for the requested period
    overlapping_request = BorrowRequest.query.filter(
        BorrowRequest.book_id == book_id,
        BorrowRequest.start_date <= end_date,
        BorrowRequest.end_date >= start_date,
        BorrowRequest.status == 'Approved'
    ).first()

    if overlapping_request:
        return jsonify({"message": "Book is not available for the requested period."}), 400

    # Create a new borrow request
    borrow_request = BorrowRequest(
        user_id=user.id,
        book_id=book_id,
        start_date=start_date,
        end_date=end_date,
        status='Approved'
    )
    
    book = Book.query.get(borrow_request.book_id)
    book.available = False
    
    db.session.add(borrow_request)
    db.session.commit()
    return jsonify({"message": "Borrow request submitted successfully."}), 201

@app.route('/requests/<int:request_id>/return', methods=['POST'])
@auth.login_required
def return_book(request_id):
    user = auth.current_user()
    if not user.is_librarian:
        return jsonify({"message": "Only librarians can mark books as returned."}), 403

    borrow_request = BorrowRequest.query.get(request_id)
    if not borrow_request:
        return jsonify({"message": "Borrow request not found."}), 404

    if borrow_request.status == 'Returned':
        return jsonify({"message": "This book is already marked as returned."}), 400

    book = Book.query.get(borrow_request.book_id)
    if not book:
        return jsonify({"message": "Book associated with this request not found."}), 404
    
    book.available = True
    borrow_request.status = 'Returned'
    db.session.commit()

    return jsonify({"message": "Book marked as returned successfully."}), 200

@app.route('/user/borrow_history', methods=['GET'])
@auth.login_required
def user_borrow_history():
    user = auth.current_user()
    borrow_requests = BorrowRequest.query.filter_by(user_id=user.id).all()
    result = [
        {
            "book_id": r.book_id,
            "start_date": r.start_date.strftime('%Y-%m-%d'),
            "end_date": r.end_date.strftime('%Y-%m-%d'),
            "status": r.status
        } 
        for r in borrow_requests
    ]

    if not result:
        return jsonify({"message" : "Borrow history not available for this user."}), 400 
    return jsonify(result), 200

# Start the server
if __name__ == '__main__':
    app.run(debug=True)