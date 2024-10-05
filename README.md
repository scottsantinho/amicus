# Amicus Project

https://github.com/user-attachments/assets/33b0c7f3-140f-406b-9f87-086374c4a966

## Table of Contents
- [Description](#description)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Description
Amicus is a web application that allows users to create and interact with personalized AI companions. Users can customize their AI's profile, engage in conversations, and track their interaction history. This project aims to provide a unique and engaging experience in AI-human interaction.

## Getting Started
To run the project locally, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/scottsantinho/amicus.git
    cd amicus_project
    ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**
    ```bash
    python manage.py migrate
    ```

5. **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

7. **Open your browser and navigate to:**
    ```
    http://127.0.0.1:8000
    ```

## Project Structure
- **amicus_project/** (main project directory)
  - **amicus_project/** (project settings)
    - `settings.py`
    - `urls.py`
    - `wsgi.py`
    - `asgi.py`
  - **nucleus/** (core functionality app)
    - `models.py`
    - `views.py`
    - `urls.py`
    - `forms.py`
    - `admin.py`
  - **colloquium/** (conversation handling app)
    - `models.py`
    - `views.py`
    - `urls.py`
    - `forms.py`
    - `admin.py`
  - **templates/**
    - **nucleus/**
      - `base.html`
      - `home.html`
      - `login.html`
      - `signup.html`
      - `profile.html`
      - `update_profile.html`
    - **colloquium/**
      - `conversation_edit.html`
      - `conversation_list.html`
      - `conversations.hmtl`
      - `conversation_detail.html`
      - `message_list.html`
      - `message.html`
      - `chat.html`
  - **static/**
    - **assets/**
      - **logo/**
        - `logo_V3.png`
    - **js/**
      - `chat.js`
  - `manage.py`
  - `requirements.txt`
  - `README.md`

## Contributing
We welcome contributions to the Amicus Project! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- **Django**: The web framework used for building this application.
- **Tailwind CSS**: For the responsive and beautiful UI design.
- **PostgreSQL**: The database system used for data storage.
- **Replicate API**: For powering the AI conversation capabilities.
- **jQuery**: For enhancing JavaScript functionality and simplifying DOM manipulation.
