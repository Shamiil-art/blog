# Blog API

Django REST Framework API for managing blog posts and comments.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Shamiil-art/blog.git
   cd blog-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Run the server:
   ```bash
   python manage.py runserver
   ```

5. Run tests:
   ```bash
   pytest blog/tests.py -v
   ```

## API Endpoints

- Register: `POST /api/users/`
- Login: `POST /api/token/`
- Posts: `GET/POST/PUT/DELETE /api/posts/`
- Comments: `GET/POST /api/posts/{id}/comments/`, `GET/PUT/DELETE /api/comments/`