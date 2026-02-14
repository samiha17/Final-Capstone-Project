# NewsApp

A Django-based news platform with **readers, journalists, editors, and publishers**. Users can subscribe to journalists or publishers, create and approve articles, and manage newsletters.  

---

## Features

- User authentication (readers, journalists, editors)
- Article management:
  - Create, edit, and delete articles (journalists)
  - Approval workflow (editors)
  - Optional publisher assignment
- Subscription system:
  - Readers can subscribe/unsubscribe to journalists or publishers
  - View subscribed articles
  - Subscribers recieve email notifications
- Newsletter management:
  - Create and update newsletters (journalists and editors)
- Admin dashboard using Django Admin:
  - Manage users, publishers, articles, and newsletters
- Role-based navigation and access control

---

## Publisher Membership & Publishing Rules

Publishers are created and managed by editors, either directly in the Django Admin interface or through the Publisher Management pages.

### Membership & Roles
- Editors and journalists are assigned to publishers either:
  - Directly by an administrator, or  
  - By journalists **requesting affiliation** and editors approving their requests.
- A journalist may belong to multiple publishers.
- Editors can **approve or deny journalist affiliation requests** from the “Pending Publisher Requests” page.

### Article Creation
- When creating an article:
  - Journalists may publish independently by leaving the publisher field empty.
  - Journalists may publish on behalf of a publisher only if they are assigned to that publisher.
- The article creation form automatically restricts the publisher selection to only those publishers the journalist belongs to.

### Affiliation Workflow
1. A journalist visits the **Publisher Requests** page and requests affiliation with a publisher.
2. Editors review pending requests on the **Pending Publisher Requests** page.
3. Editors approve a request:
   - The journalist is added to the publisher.
   - The request is marked as approved.
4. Once approved, the journalist can publish articles under that publisher.


---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/samiha17/Final-Capstone-Project.git
   cd Final-Capstone-Project/news_project
   ```

---

## OPTION A: Run Locally

1. **Ensure MySQL Server is Running:**
   ```bash
   mysql -u root -p
   ```

2. **Create MySQL database:**

   Login to your MySQL server and create the database:

   ```sql
   CREATE DATABASE news_db;
   ```
3. **Update database credentials in `news_project/settings.py`** if your MySQL username or password differ:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'news_db',
           'USER': 'root',
           'PASSWORD': 'your_mysql_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

4. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

5. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

6. **Upgrade pip and install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. **Apply migrations (only after MySQL is running and the database exists):**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
8. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

9. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
* Open your browser and go to:  
   http://127.0.0.1:8000/

10. **Deactivate the virtual environment when finished:**
   ```bash
   deactivate
   ```   
---

## Option B: Run with Docker

**Ensure you are inside the `news_project` directory (where Dockerfile and manage.py are located) before running these commands.**


1. **Build the Docker image:**
   ```bash
   docker build -t newsapp .
   ```

2. **Run the Docker container:**
   ```bash
   docker run -p 8000:8000 newsapp
   ```

3. **Access the application:**

* Open your browser and go to: 
   http://127.0.0.1:8000/

---

## Usage
  * Users
      * Login at `/login/`
      * Register at `/register/`
  * Reader
      * Browse all articles: `/articles/`
      * View subscribed articles: `/articles/subscribed/`
      * Manage subscriptions: `/subscriptions/`
      * View newsletters: `/newsletters/`
  * Journalist
      * Create articles: `/articles/create/`
      * Update own articles: `/articles/<id>/update/`
      * Create newsletters: `/newsletters/create/`
  * Editor
      * Review pending articles: `/editor/articles/pending/`
      * Approve articles
      * Create and update newsletters
  * Publisher
      * Created via Django Admin
      * Assign editors and journalists
      * Articles can be linked to a publisher

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/articles/` | `GET` | Return a list of all approved articles |
| `/api/articles/subscribed/` | `GET` | Return articles only from the reader’s subscribed publishers/journalists |
| `/api/articles/<id>/` | `GET` | Retrieve a single article |
| `/api/articles/` | `POST` | Create a new article (journalists only) |
| `/api/articles/<id>/` | `PUT` | Update an article (editors/journalists) |
| `/api/articles/<id>/` | `DELETE` | Delete an article (editors/journalists) |

---

## Authentication

Uses Token-based authentication from Django REST Framework

* To obtain a token for a user:
   ```bash
      python manage.py drf_create_token <username>
   ```
* Include the token in curl requests:
   ```bash
      -H "Authorization: Token YOUR_TOKEN_HERE"
   ```

---

## Running Tests

   ```bash
      python manage.py test
   ```
