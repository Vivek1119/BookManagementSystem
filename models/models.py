# =============================================================================================
#                                             Models
# =============================================================================================

#inbuilt import
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

#local import
from database.database import db


class Book(db.Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))
    year_published = Column(Integer)
    summary = Column(Text)

    # Establish relationship with Review
    reviews = relationship("Review", back_populates="book", cascade="all, delete")


class Review(db.Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)
    review_text = Column(Text)
    rating = Column(Integer, nullable=False)

    # Relationship back to Book
    book = relationship("Book", back_populates="reviews")