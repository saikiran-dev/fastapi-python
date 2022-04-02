from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor

app = FastAPI()

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
def create_post(newPost: Post):
    post = newPost.dict()
    post['id'] = randrange(0,1000000)
    my_posts.append(post)
    return {"data": post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = getPostById(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not Found")
    return {"data": post}
