# Graduation Project: Online Educational Platform

This project is an advanced online educational platform designed to enhance programming skills for students of all levels. The platform offers a user-friendly content management system, personalized learning experiences, and intelligent recommendation features.

---

## Key Features

### 1. **Dynamic Website Management**
- Developed a dynamic editor page that allows site moderators to effortlessly create, edit, and manage course content with tools resembling Microsoft Word.
- Enabled seamless management of courses and quizzes without requiring coding knowledge, empowering moderators to focus on high-quality content delivery.

### 2. **Helper System**
- Introduced an intelligent system that recommends the most suitable starting chapters for learners based on an initial assessment quiz.
- Personalized learning paths are tailored to the learner's current knowledge and skill level, ensuring a smooth and effective learning journey.

### 3. **Recommender System**
- We created a content-based recommender system that suggests courses aligning with the learner's preferences, previous knowledge, and learning style.
- This feature enhances efficiency and ensures a tailored learning experience.

---
## Getting Started

### Prerequisites
Before running the project, make sure you have the following installed:
- Python 3.8 or higher
- Django 4.0 or higher
- Git (for cloning the repository)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Ahmad-Jaber0/Graduation-project.git
   cd your-repository
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   ```

3. **Install Required Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**
   - Configure the `DATABASES` settings in `settings.py` to match your database (if not using SQLite).
   - Run the following commands to apply migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

5. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Platform**
   Open your browser and go to:  
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
---

## Project Resources

### Project Demo Video
[Watch the demo here](https://www.youtube.com/watch?v=W7-nJvsSWBI)

### System Design

#### Entity-Relationship Diagram (ERD)
![ERD Diagram](https://github.com/user-attachments/assets/3eea6e2f-2527-4ad9-9cf5-dac92328e19c)

#### Class Diagram
![Class Diagram](https://github.com/user-attachments/assets/2b686661-87d4-4e9d-956a-27a86f2ac9b3)

---

## Use Case Diagrams

### Admin Use Case
![Admin Use Case](https://github.com/user-attachments/assets/6c2d9664-2d3f-4a99-9dca-43964cd0f483)

### Learner Use Case
![Learner Use Case](https://github.com/user-attachments/assets/f56d7662-ecb7-43e9-be7c-4f3a95a27eb0)

### Moderator Use Case
![Moderator Use Case](https://github.com/user-attachments/assets/9e557268-fb79-44a1-b196-ee7c38532eec)

---

## Analysis Documents

### Helper System Analysis
[Read the detailed analysis](https://stirring-parmesan-c8c.notion.site/C-Quiz-2-dfa4ecd664004fc48e29d1b76a747813?pvs=4)

### Recommender System Analysis
[Explore the recommender system analysis](https://stirring-parmesan-c8c.notion.site/Outer-Recommender-59ba69e1e65340d78fec912369419949)

---

## Technologies Used
- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript
- **Version Control**: Git & GitHub

---

Feel free to explore the platform or reach out for further details about the project!
