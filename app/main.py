from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

try:
    conn = psycopg2.connect(host = 'localhost', database='', user='', password='', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("database is connected")
except Exception as error:
    print(error)
    time.sleep(2)

my_posts = []

def getPostById(id):
    for p in my_posts:
        if p['id'] == id:
            return  p

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/create-post")
def create_post(post: Post):
    # post = newPost.dict()
    # post['id'] = randrange(0,1000000)
    # my_posts.append(post)
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.delete("/posts/{id}")
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post does not exist")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id),))
    updated_post = cursor.fetchone()
    conn.commit()
    
    if updated_post == None:
        raise HTTPException (status_code =  status.HTTP_404_NOT_FOUND, detail = f"post doest not exist")
    return {"data": updated_post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = getPostById(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not Found")
    return {"data": post}
