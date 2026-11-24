# Name: Cauy Whaley
# File: book_api.py
# Description: A Flask CRUD API for storing book information in a SQLite database.

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    publisher = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "book_name": self.book_name,
            "author": self.author,
            "publisher": self.publisher,
        }


def book_fields(data, required=True):
    """Validate the JSON fields sent to create or update a book."""
    if not isinstance(data, dict):
        return None, "Send a JSON object containing book details."

    names = ("book_name", "author", "publisher")
    if required and any(name not in data for name in names):
        return None, "book_name, author, and publisher are required."

    values = {}
    for name in names:
        if name in data:
            value = data[name]
            if not isinstance(value, str) or not value.strip():
                return None, f"{name} must be a non-empty string."
            if len(value.strip()) > 150:
                return None, f"{name} must be 150 characters or fewer."
            values[name] = value.strip()
    if not required and not values:
        return None, "Provide at least one book field to update."
    return values, None


@app.route("/books", methods=["GET"])
def get_books():
    books = db.session.execute(db.select(Book).order_by(Book.id)).scalars().all()
    return jsonify([book.to_dict() for book in books]), 200


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        return jsonify({"error": "Book not found."}), 404
    return jsonify(book.to_dict()), 200


@app.route("/books", methods=["POST"])
def create_book():
    fields, error = book_fields(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    book = Book(**fields)
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        return jsonify({"error": "Book not found."}), 404

    fields, error = book_fields(request.get_json(silent=True), required=False)
    if error:
        return jsonify({"error": error}), 400

    for name, value in fields.items():
        setattr(book, name, value)
    db.session.commit()
    return jsonify(book.to_dict()), 200


@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        return jsonify({"error": "Book not found."}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully."}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
