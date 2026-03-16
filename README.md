# ISLA-Student-Learning-App
# 🤖 AI-Powered Smart Learning Assistant

An AI-driven smart learning system designed to improve the learning experience using multiple intelligent agents. The system analyzes user performance, emotions, and learning patterns to provide personalized tutoring, quizzes, recommendations, and adaptive learning strategies.

This project demonstrates the implementation of a multi-agent AI architecture for intelligent educational systems.

---

## 📌 Features

* **AI Tutor Agent**
  Provides learning guidance and explanations for different topics.

* **Memory Agent**
  Stores and tracks user learning progress and interaction history.

* **Quiz Agent**
  Generates quizzes to test user knowledge and understanding.

* **Evaluation Agent**
  Evaluates quiz answers and provides feedback.

* **Recommendation Agent**
  Suggests new learning topics based on performance.

* **Emotion Agent**
  Detects user emotions and adapts learning difficulty.

* **Spaced Learning Agent**
  Uses spaced repetition techniques to improve long-term memory.

* **Orchestrator System**
  Manages communication between all AI agents.

---

## 🏗️ Project Structure

```
Project
│
├── backend
│   ├── agents
│   │   ├── emotion_agent.py
│   │   ├── evaluation_agent.py
│   │   ├── memory_agent.py
│   │   ├── quiz_agent.py
│   │   ├── recommendation_agent.py
│   │   ├── spaced_agent.py
│   │   ├── tutor_agent.py
│   │   └── user_agent.py
│   │
│   ├── utils
│   │   └── difficulty_engine.py
│   │
│   ├── database.py
│   ├── models.py
│   ├── schema.py
│   ├── orchestrator.py
│   ├── logger.py
│   └── main.py
│
└── README.md
```

---

## ⚙️ Technologies Used

* Python
* Artificial Intelligence Concepts
* Multi-Agent System Architecture
* Database Integration
* Modular Backend Design

---

## 🚀 Installation

### 1. Clone the Repository

```
git clone https://github.com/yourusername/project-name.git
cd project-name
```

### 2. Create Virtual Environment

```
python -m venv venv
```

Activate the environment

**Windows**

```
venv\Scripts\activate
```

**Linux / Mac**

```
source venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Run the Project

```
python backend/main.py
```

---

## 🧠 How the System Works

1. The User Agent receives input from the user.
2. The Orchestrator coordinates communication between all agents.
3. Different agents perform specific tasks such as tutoring, quiz generation, evaluation, and recommendations.
4. The system adapts learning strategies based on user performance and feedback.

This architecture enables a personalized adaptive learning experience.

---

## 📊 Use Cases

* AI-powered learning assistants
* Smart e-learning platforms
* Adaptive tutoring systems
* Intelligent quiz generation systems
* Personalized education platforms

---

## 🔮 Future Improvements

* Web interface using Flask or React
* Integration with large language models (LLMs)
* Real-time emotion detection
* Student analytics dashboard
* Cloud deployment

---

## 👨‍💻 Author

Sahil Salunke
Information Technology & Artificial Intelligence Student

---

## ⭐ Contributing

Contributions are welcome. Feel free to fork the repository and submit pull requests to improve the project.
