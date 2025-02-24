
# Book Managment System

This app is developed to manage books and its respective informations.

# Git repo:

https://github.com/Vivek1119/BookManagementSystem


# Tools required:

Python 3.9 +

# Steps

* Clone the repository git@github.com:Vivek1119/BookManagementSystem.git

## Execute

```bash
  cd BookManagementSystem
```

* create virtual environment using below command inside project

    windows: 
    
        python -m venv bmsvenv
    
    ubuntu: 
        
        sudo apt install python3-venv
        python3 -m venv newvenv
    


## Installation

Install project specific libraries using requirement.txt with npm

```bash
  pip install -r requirement.txt
```

Add Postgrese Database Details in .env file

```
DB_USER=""
DB_PASS=""
DB_HOST=""
DB_PORT=""
DB_NAME=""
SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
USERNAME = ""
FULL_NAME = ""
EMAIL = ""
HASHED_PASSWORD = ""
DISABLE = False/True
```

Create Table in Postgrese Database

```
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    year_published INT,
    summary TEXT
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    review_text TEXT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
```

## Run Command

```
  uvicorn app:app --reload
```


    
