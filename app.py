# =============================================================================================
#                                       BookManagementSystem
# =============================================================================================

#inbuilt import
import uvicorn
from pydantic import BaseModel
from datetime import timedelta
from typing import List, Annotated
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, Depends, status, HTTPException


#local import
from database.database import db
from models.models import Book, Review
from helper.oauth_helper import (authenticate_user, create_access_token, fake_users_db,
                                 User, get_current_active_user, Token, ACCESS_TOKEN_EXPIRE_MINUTES)
router = APIRouter(prefix="/api/v1", tags=["Books"])


app = FastAPI(title="Book Management System",
              version="v1"
              )

@asynccontextmanager
async def lifespan(app):
    await db.connect_db()
    yield


class Books(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    year_published: int
    summary: str


class Reviews(BaseModel):
    user_id: int
    review_text: str
    rating: int


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/book")
async def add_book(book: Books,
                   current_user: Annotated[User, Depends(get_current_active_user)],
                   session: AsyncSession = Depends(db.get_session),
                   ):
    """
    :param current_user: authenticate user for allowing to use api  \n
    :param book: object which hold information of the book details \n
    :param session: session to perform database operation \n
    :return: book details in json format on success
    """
    try:
        book_data = Book(
            id=book.id,
            title=book.title,
            author=book.author,
            genre=book.genre,
            year_published=book.year_published,
            summary=book.summary)
        session.add(book_data)
        await session.commit()
        await session.refresh(book_data)
        return book_data
    except Exception as e:
        print(f"Exception {e} occurred while creating book instance")


@router.get("/books", response_model=List[Books])
async def get_all_books(current_user: Annotated[User, Depends(get_current_active_user)],
        session: AsyncSession = Depends(db.get_session)):
    """
    :param current_user: authenticate user for allowing to use api  \n
    :param session: session to perform database operation \n
    :return: retrieve all books stored in database
    """
    try:
        result  = await session.execute(select(Book))
        books = result.scalars().all()
        return books
    except Exception as e:
        print(f"Exception {e} occurred while retrieving all books")


@router.get("/books/{book_id}", response_model=List[Books])
async def get_book(book_id: int,
                   current_user: Annotated[User, Depends(get_current_active_user)],
                   session: AsyncSession = Depends(db.get_session)):
    """
    :param current_user: authenticate user for allowing to use api  \n
    :param book_id: book id to retrieve its details \n
    :param session: session to perform database operation \n
    :return: book details
    """
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = [result.scalars().first()]
        if not book:
            return JSONResponse(content={"message": f"Book id {book_id} not found"},
                                status_code=status.HTTP_404_NOT_FOUND)
        return book
    except Exception as e:
        print(f"Exception {e} occurred in retrieving book {book_id}")


@router.put("/books/{book_id}", response_model=Books)
async def update_book(book_id: int, book_update: Books,
                      current_user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(db.get_session)):
    """
    :param book_id: book id to update it details \n
    :param book_update: book object to update its details \n
    :param current_user: authenticate user for allowing to use api  \n
    :param session: session to perform database operation \n
    :return: details of book which has been updated successfully
    """
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        update_data = book_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(book, key, value)

        await session.commit()
        await session.refresh(book)
        return book
    except Exception as e:
        print(f"exception {e} occurred in updating book {book_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/books/{book_id}", response_model=dict)
async def delete_book(book_id: int,
                      current_user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(db.get_session)):
    """
    :param book_id: book id to delete from database \n
    :param current_user: authenticate user for allowing to use api  \n
    :param session: session to perform database operation \n
    :return: message if book get successfully deleted
    """
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        await session.delete(book)
        await session.commit()
        return {"message": f"Book with ID {book_id} has been deleted successfully"}
    except Exception as e:
        print(f"exception {e} occurred in deleting book {book_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/books/{book_id}/reviews/", response_model=Reviews)
async def add_review(book_id: int, review: Reviews,
                     current_user: Annotated[User, Depends(get_current_active_user)],
                     session: AsyncSession = Depends(db.get_session)):
    """
    :param book_id: book id to update the review in the database \n
    :param review: review of the book \n
    :param current_user: authenticate user for allowing to use api  \n
    :param session: session to update review in database \n
    :return: review details of book
    """
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        db_review = Review(
            book_id=book_id,
            user_id=review.user_id,
            review_text=review.review_text,
            rating=review.rating
        )
        session.add(db_review)
        await session.commit()
        await session.refresh(db_review)
        return db_review
    except Exception as e:
        print(f"exception {e} occurred in fetching review of the book {book_id}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/books/{book_id}/reviews/", response_model=List[Reviews])
async def get_reviews(book_id: int,
                      current_user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(db.get_session)):
    """
    :param book_id: book id to retrieve the review \n
    :param current_user: authenticate user for allowing to use api  \n
    :param session: session to update review in database \n
    :return: review of the specific book
    """
    try:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        reviews_result = await session.execute(select(Review).where(Review.book_id == book_id))
        reviews = [reviews_result.scalars().first()]
        return reviews
    except Exception as e:
        print(f"exception {e} occurred in fetching review of the book {book_id}")
        raise HTTPException(status_code=500, detail="Internal server error")



app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(app, reload=True)

