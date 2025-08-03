# RealtyTwin - AI-Powered Real Estate Command Center

RealtyTwin is an intelligent, AI-powered command center for real estate agents, designed to streamline operations, automate tasks, and provide data-driven insights. It acts as a digital twin for a real estate business, with a special focus on the Palm Jumeirah market in Dubai.

## Features

*   **AI Assistant (AURA):** A conversational AI assistant that can answer questions, create tasks, find property owners, and more.
*   **Data Hub:** Upload and manage all your real estate documents, including contracts, listings, and contact lists.
*   **Knowledge Base:** A centralized repository of all your data, including property details, contact information, and market trends.
*   **Automated Workflows:** Automatically generate follow-up emails, score leads, and find matching buyers for your properties.
*   **Advanced Analytics:** Get real-time insights into your performance, market trends, and lead engagement.

## Getting Started

### Prerequisites

*   Python 3.10 or higher
*   pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```
    git clone https://github.com/trentthakid/wesleykatez.git
    ```
2.  **Navigate to the project directory:**
    ```
    cd RealtyTwin
    ```
3.  **Create a virtual environment:**
    ```
    python -m venv .venv
    ```
4.  **Activate the virtual environment:**
    *   **Windows:**
        ```
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```
        source .venv/bin/activate
        ```
5.  **Install the required packages:**
    ```
    pip install -r requirements.txt
    ```

## Usage

1.  **Set up your environment variables:**
    *   Create a file named `.env` in the root of the project.
    *   Add your Gemini API key to the `.env` file:
        ```
        GEMINI_API_KEY=your_api_key_here
        ```
2.  **Run the application:**
    ```
    python app.py
    ```
3.  **Open your browser** and navigate to `http://127.0.0.1:5000` to access the application.

## Project Structure

*   **`app.py`:** The main Flask application file.
*   **`database.py`:** Handles all database interactions.
*   **`gemini_integration.py`:** Manages all interactions with the Gemini AI model.
*   **`knowledge_base.py`:** Handles document processing, entity recognition, and information retrieval.
*   **`automation.py`:** Contains the business logic for automating common tasks.
*   **`analytics.py`:** Contains the business logic for analyzing your data and providing insights.
*   **`static/`:** Contains the frontend files (HTML, CSS, and JavaScript).
*   **`uploads/`:** The default folder for file uploads.
*   **`knowledge/`:** Contains the JSON files that make up the core knowledge base.

## How It Works: Application Architecture

RealtyTwin is built on a modular architecture that separates concerns and allows for easy expansion. Here's a breakdown of how the different components work together:

### 1. Frontend (`static/`)

The user interface is a single-page application (SPA) built with HTML, CSS, and Vue.js. It communicates with the backend via a REST API.

*   **`index.html`:** The main entry point for the application.
*   **`style.css`:** Contains all the styling for the application.

### 2. Backend (`app.py`)

The backend is a Flask application that serves as the central hub for the entire system. It handles all incoming requests from the frontend and orchestrates the interactions between the other components.

*   **API Endpoints:** Exposes a series of API endpoints (e.g., `/api/chat`, `/api/properties`, `/api/contacts`) that the frontend can call to send and receive data.
*   **Request Handling:** When a request comes in, `app.py` determines which function to call to handle it. For example, a request to `/api/chat` is routed to the `chat()` function, which in turn calls the `route_command()` function to process the user's message.

### 3. The Brains: Two-Tier Cognitive Engine (`app.py` and `gemini_integration.py`)

The core of the AI assistant is a two-tier cognitive engine that's designed to be both fast and intelligent:

*   **Tier 0: Simple Responses (`app.py`):** The system first checks for simple, conversational inputs like "thanks" or "ok" and provides a canned response. This is fast and avoids unnecessary calls to the AI model.
*   **Tier 1: Intent Recognition (`gemini_integration.py`):** If the input is more complex, the system sends it to the Gemini AI model to determine the user's intent (e.g., `find_owner`, `create_task`).
*   **Tier 2: Tool-Based Routing (`app.py`):** Based on the intent, the system calls the appropriate function to handle the request (e.g., `find_owner()`, `create_task()`).
*   **Tier 3: LLM Escalation (`gemini_integration.py`):** If the intent is unknown, the system escalates the query to the Gemini model for a more general, conversational response.

### 4. The Memory: Knowledge Base (`knowledge_base.py` and `database.py`)

The knowledge base is the application's memory. It's made up of two main components:

*   **Structured Data (`knowledge/`):** The JSON files in the `knowledge/` directory contain structured data about the Palm Jumeirah market. This data is loaded into memory when the application starts and is used to provide quick, accurate answers to common questions.
*   **Unstructured Data (`database.py`):** The documents you upload are processed by the `knowledge_base.py` module and stored in the `KnowledgeNexus` table in the database. The system automatically extracts key information from these documents and makes it available to the AI assistant.
*   **Database (`database.py`):** The application uses an SQLite database to store all of its data, including properties, contacts, deals, and tasks. The `database.py` module provides a set of functions for interacting with the database.

### 5. The Engine Room: Automation and Analytics (`automation.py` and `analytics.py`)

These modules contain the business logic for the application:

*   **`automation.py`:** Contains functions for automating common tasks, such as generating follow-up emails, finding matching buyers, and getting overdue tasks.
*   **`analytics.py`:** Contains functions for analyzing your data and providing insights, such as scoring leads, getting performance metrics, and predicting deal probability.

### Data Flow Example: "Who owns Palm Tower Unit 3401?"

1.  The user types "who owns palm tower unit 3401?" into the chat interface and clicks "send."
2.  The frontend sends a POST request to the `/api/chat` endpoint in `app.py`.
3.  The `chat()` function calls the `route_command()` function to process the message.
4.  `route_command()` sends the message to the `get_intent()` function in `gemini_integration.py`.
5.  The Gemini model returns the intent `find_owner`.
6.  `route_command()` calls the `find_owner()` function in `app.py`.
7.  `find_owner()` calls the `find_properties_in_text()` function in `knowledge_base.py` to identify the property.
8.  `find_owner()` then queries the database (via `database.py`) to find the owner of the property.
9.  The owner's information is returned to the frontend and displayed in the chat interface.

### Detailed Feature Explanation

#### AI Assistant (AURA)

AURA is the conversational AI assistant that serves as the primary interface for the application. It's designed to understand natural language queries and respond with accurate, relevant information.

*   **Intent Recognition:** AURA uses the Gemini AI model to determine the user's intent. This allows it to understand what the user is trying to do and respond accordingly.
*   **Entity Extraction:** AURA can extract key information from the user's query, such as property names, contact names, and dates. This allows it to perform more specific and accurate actions.
*   **Tool-Based Routing:** Based on the user's intent, AURA will call the appropriate function to handle the request. This allows it to perform a wide range of actions, from finding property owners to creating tasks.
*   **Conversational Fallback:** If AURA is unable to determine the user's intent, it will fall back to a more general, conversational mode. This allows it to handle a wider range of queries and provide a more natural user experience.

#### Data Hub

The Data Hub is where you can upload and manage all of your real estate documents.

*   **File Upload:** You can upload a wide range of file types, including PDFs, Word documents, Excel spreadsheets, and CSV files.
*   **Automatic Processing:** When you upload a file, the system automatically processes it and adds its content to the knowledge base.
*   **Intelligent CSV Handling:** The system can automatically detect the type of data in a CSV file and process it accordingly. For example, if you upload a CSV file of contacts, the system will automatically add them to the `Contacts` table. If you upload a CSV file of property owners, the system will automatically link them to their properties.

#### Knowledge Base

The knowledge base is the heart of the application. It's a centralized repository of all your data, including property details, contact information, and market trends.

*   **Structured Data:** The knowledge base includes a set of JSON files that contain structured data about the Palm Jumeirah market. This data is used to provide quick, accurate answers to common questions.
*   **Unstructured Data:** The knowledge base also includes all of the documents you've uploaded. The system automatically extracts key information from these documents and makes it available to the AI assistant.
*   **Database:** All of the data in the knowledge base is stored in an SQLite database. This makes it easy to query and analyze your data.

#### Automated Workflows

The application includes a number of automated workflows that are designed to save you time and effort.

*   **Follow-up Tasks:** The system automatically generates a prioritized list of follow-up tasks based on the lead status and last contact date of your contacts.
*   **Matching Buyers:** The system can automatically find potential buyers for a given property based on their profile and preferences.
*   **Follow-up Emails:** The system can automatically draft personalized follow-up emails for your contacts.

#### Advanced Analytics

The application includes a number of advanced analytics tools that are designed to help you make better, more informed decisions.

*   **Lead Scoring:** The system automatically scores all of your leads based on a variety of factors, including their lead status, source, and engagement level.
*   **Market Insights:** The system can provide you with real-time insights into the real estate market, including average prices, transaction volumes, and market trends.
*   **Performance Metrics:** The system can provide you with a detailed overview of your performance, including your conversion rate, average deal size, and task completion rate.
*   **Deal Probability:** The system can predict the probability of a deal closing based on a variety of factors, including the lead's score, the property's price, and the age of the deal.
