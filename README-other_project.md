# Learning Log

![Screenshot 2024-09-01 at 2 27 23 PM](https://github.com/user-attachments/assets/32c66eea-1ef4-494b-a792-cb79e5af5851)


## Table of Contents
- [Description](#description)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Description
Learning Log is a web application that allows users to log and track their learning progress. Users can create topics and make entries under each topic to document what they have learned. This project is inspired by the "Python Crash Course" by Eric Matthes.

## Getting Started
To run the project locally, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/learning_log.git
    cd learning_log
    ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv ll_env
    source ll_env/bin/activate  # On Windows use `ll_env\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**
    ```bash
    python manage.py migrate
    ```

5. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

6. **Open your browser and navigate to:**
    ```
    http://127.0.0.1:8000
    ```

## Project Structure
- **learning_log/**
  - **.platform/**
    - **local/**
      - `.gitignore`
      - `project.yaml`
      - `README.txt`
      - `routes.yaml`
      - `services.yaml`
  - **accounts/**
    - **migrations/**
    - **templates/registration/**
      - `login.html`
      - `register.html`
    - `__init__.py`
    - `admin.py`
    - `apps.py`
    - `models.py`
    - `tests.py`
    - `urls.py`
    - `views.py`
  - **learning_logs/**
    - **migrations/**
    - **static/learning_logs/assets/**
      - `logo_learning_log.png`
    - **templates/learning_logs/**
      - `base.html`
      - `edit_entry.html`
      - `index.html`
      - `new_entry.html`
      - `new_topic.html`
      - `topic.html`
      - `topics.html`
    - `__init__.py`
    - `admin.py`
    - `apps.py`
    - `forms.py`
    - `models.py`
    - `tests.py`
    - `urls.py`
    - `views.py`
- **ll_project/**
  - **templates/**
    - `.gitignore`
    - `.platform.app.yaml`
    - `db.sqlite3`
    - `manage.py`
    - `README.md`
    - `requirements_remote.txt`
    - `requirements.txt`

## Contributing
While Learning Log is a modest project, I am very much open to contributions! If you'd like to contribute, here's how:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- **Eric Matthes**: Whose project in "Python Crash Course" served as the inspiration for this small web application.
- **Cursor.ai and Claude 3.5 Sonnet**: For assistance in refactoring, commenting the code, and writing this beautiful README.md!
- **DALLE-3**: For the logo.
