from typing import Annotated, Generator
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from db.database import SessionLocal


app = FastAPI()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/authors/", response_model=list[schemas.AuthorList])
def read_authors(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return crud.get_all_authors(db=db, skip=skip, limit=limit)


@app.get("/authors/{author_id}/", response_model=schemas.AuthorBase)
def read_single_author(
    author_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    db_author = crud.get_author_by_id(db=db, author_id=author_id)
    if not db_author:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )
    return db_author


@app.post("/authors/", response_model=schemas.AuthorBase)
def create_author(
    author: schemas.AuthorCreate,
    db: Annotated[Session, Depends(get_db)]
):
    db_author = crud.get_author_by_name(
        db=db,
        name=author.name
    )
    if db_author:
        raise HTTPException(
            status_code=404,
            detail="Author with this name already exists"
        )
    return crud.create_author(
        db=db,
        author=author
    )


@app.get("/books/", response_model=list[schemas.BookList])
def read_books(
    skip: int = 0,
    limit: int = 10,
    author_id: int = None,
    db: Session = Depends(get_db)
):
   return crud.get_books_list(
       db=db, skip=skip, limit=limit, author_id=author_id
   )


@app.post("/books/", response_model=schemas.BookBase)
def create_book(
    book: schemas.BookCreate,
    db: Annotated[Session, Depends(get_db)]
):
    db_book = crud.get_book_by_title(
        db=db, title=book.title
    )
    if db_book:
        raise HTTPException(
            status_code=404,
            detail="Book with this title already exists"
        )
    author = crud.get_author_by_id(
        db=db, author_id=book.author_id
    )
    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )
    return crud.create_book(
        db=db, book=book
    )
