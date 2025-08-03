# RealtyTwin - Technical Guide

This document provides a detailed technical explanation of the RealtyTwin application, including its architecture, database schema, and core components.

## 1. Database Schema (`database.py`)

The application uses an SQLite database to store all of its data. The schema is designed to be both flexible and scalable, and it's divided into three main categories: core operational tables, intelligence tables, and automation tables.

### 1.1 Core Operational Tables

These tables are the foundation of the application and are used to store the core data for the real estate business.

#### `Properties`

This table stores all of the properties in the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `building` | TEXT | The name of the building or community. |
| `unit` | TEXT | The unit number. |
| `area` | TEXT | The area where the property is located (e.g., Palm Jumeirah). |
| `property_type` | TEXT | The type of property (e.g., Apartment, Villa). |
| `bedrooms` | INTEGER | The number of bedrooms. |
| `bathrooms` | INTEGER | The number of bathrooms. |
| `size_sqft` | REAL | The size of the property in square feet. |
| `price` | REAL | The price of the property. |
| `status` | TEXT | The current status of the property (e.g., Available, Sold). |
| `description` | TEXT | A detailed description of the property. |
| `amenities` | TEXT | A list of the amenities available with the property. |
| `created_date` | TEXT | The date the property was added to the system. |
| `updated_date` | TEXT | The date the property was last updated. |

#### `Contacts`

This table stores all of the contacts in the system, including leads, clients, and property owners.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `name` | TEXT | The name of the contact. |
| `email` | TEXT | The email address of the contact. |
| `phone` | TEXT | The phone number of the contact. |
| `lead_status` | TEXT | The current status of the lead (e.g., Hot, Warm, Cold). |
| `source` | TEXT | The source of the lead (e.g., Referral, Website). |
| `notes` | TEXT | Any notes about the contact. |
| `last_contacted_date` | TEXT | The date the contact was last contacted. |
| `created_date` | TEXT | The date the contact was added to the system. |
| `updated_date` | TEXT | The date the contact was last updated. |

#### `Deals`

This table stores all of the deals in the system, both active and closed.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `property_id` | INTEGER | A foreign key that links to the `Properties` table. |
| `contact_id` | INTEGER | A foreign key that links to the `Contacts` table. |
| `deal_type` | TEXT | The type of deal (e.g., Sale, Rent). |
| `status` | TEXT | The current status of the deal (e.g., Active, Closed). |
| `deal_value` | REAL | The value of the deal. |
| `commission` | REAL | The commission earned from the deal. |
| `created_date` | TEXT | The date the deal was created. |
| `closing_date` | TEXT | The date the deal was closed. |
| `notes` | TEXT | Any notes about the deal. |

#### `Tasks`

This table stores all of the tasks in the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `title` | TEXT | The title of the task. |
| `description` | TEXT | A detailed description of the task. |
| `status` | TEXT | The current status of the task (e.g., Pending, In Progress, Completed). |
| `priority` | TEXT | The priority of the task (e.g., High, Medium, Low). |
| `assigned_to` | TEXT | The person the task is assigned to. |
| `contact_id` | INTEGER | A foreign key that links to the `Contacts` table. |
| `property_id` | INTEGER | A foreign key that links to the `Properties` table. |
| `created_date` | TEXT | The date the task was created. |
| `due_date` | TEXT | The date the task is due. |
| `completed_date` | TEXT | The date the task was completed. |

#### `ContactProperties`

This is a junction table that links contacts to properties and defines their relationship.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `contact_id` | INTEGER | A foreign key that links to the `Contacts` table. |
| `property_id` | INTEGER | A foreign key that links to the `Properties` table. |
| `relationship_type` | TEXT | The relationship between the contact and the property (e.g., Owner, Interested, Viewing Scheduled). |
| `start_date` | TEXT | The start date of the relationship. |
| `end_date` | TEXT | The end date of the relationship. |
| `created_date` | TEXT | The date the relationship was created. |

### 1.2 Intelligence Tables

These tables are used to store data for the application's more advanced features, such as market analysis and lead scoring.

#### `HistoricalTransactions`

This table stores historical transaction data, which is used to generate market insights.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `property_id` | INTEGER | A foreign key that links to the `Properties` table. |
| `transaction_type` | TEXT | The type of transaction (e.g., Sale, Rent). |
| `price` | REAL | The price of the transaction. |
| `transaction_date` | TEXT | The date of the transaction. |
| `buyer_name` | TEXT | The name of the buyer. |
| `seller_name` | TEXT | The name of the seller. |
| `agent_commission` | REAL | The commission earned from the transaction. |
| `market_conditions` | TEXT | The market conditions at the time of the transaction. |
| `created_date` | TEXT | The date the transaction was added to the system. |

#### `MasterOwners`

This table stores consolidated ownership data, which is used to provide a single source of truth for property ownership.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `property_id` | INTEGER | A foreign key that links to the `Properties` table. |
| `owner_name` | TEXT | The name of the owner. |
| `owner_email` | TEXT | The email address of the owner. |
| `owner_phone` | TEXT | The phone number of the owner. |
| `ownership_percentage` | REAL | The owner's percentage of ownership. |
| `confidence_score` | REAL | A score that represents the confidence in the accuracy of the ownership data. |
| `data_source` | TEXT | The source of the ownership data. |
| `verified` | BOOLEAN | Whether the ownership data has been verified. |
| `created_date` | TEXT | The date the ownership data was added to the system. |
| `updated_date` | TEXT | The date the ownership data was last updated. |

#### `KnowledgeNexus`

This table stores all of the unstructured data in the knowledge base, including the content of uploaded documents.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `content_type` | TEXT | The type of content (e.g., document, text, data). |
| `title` | TEXT | The title of the content. |
| `content` | TEXT | The full text of the content. |
| `embedding_vector` | BLOB | The embedding vector for the content, which is used for semantic search. |
| `source_file` | TEXT | The name of the file the content was extracted from. |
| `metadata` | TEXT | A JSON object that contains metadata about the content. |
| `tags` | TEXT | A comma-separated list of tags for the content. |
| `created_date` | TEXT | The date the content was added to the system. |
| `updated_date` | TEXT | The date the content was last updated. |

### 1.3 Automation Tables

These tables are used to support the application's automation features.

#### `EmailTemplates`

This table stores email templates that can be used to send automated emails.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `template_name` | TEXT | The name of the template. |
| `subject` | TEXT | The subject of the email. |
| `body` | TEXT | The body of the email. |
| `template_type` | TEXT | The type of template (e.g., follow_up, welcome). |
| `variables` | TEXT | A comma-separated list of the variables that can be used in the template. |
| `created_date` | TEXT | The date the template was created. |
| `updated_date` | TEXT | The date the template was last updated. |

#### `MarketData`

This table stores market data, which is used to generate market insights.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `area` | TEXT | The area the market data is for. |
| `property_type` | TEXT | The type of property the market data is for. |
| `average_price` | REAL | The average price of properties in the area. |
| `median_price` | REAL | The median price of properties in the area. |
| `price_per_sqft` | REAL | The average price per square foot in the area. |
| `total_transactions` | INTEGER | The total number of transactions in the area. |
| `market_trend` | TEXT | The current market trend (e.g., Up, Down, Stable). |
| `data_date` | TEXT | The date the market data was collected. |
| `created_date` | TEXT | The date the market data was added to the system. |

#### `LeadScores`

This table stores the scores for each lead, which are calculated by the lead scoring algorithm.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `contact_id` | INTEGER | A foreign key that links to the `Contacts` table. |
| `score` | INTEGER | The score for the lead. |
| `score_factors` | TEXT | A JSON object that contains a breakdown of the score. |
| `last_calculated` | TEXT | The date the score was last calculated. |

#### `ConversationHistory`

This table stores the history of all conversations with the AI assistant.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | The primary key for the table. |
| `session_id` | TEXT | The ID of the session. |
| `role` | TEXT | The role of the person who sent the message (e.g., user, assistant). |
| `content` | TEXT | The content of the message. |
| `created_date` | TEXT | The date the message was sent. |

## 3. AI Assistant (AURA)

AURA is the conversational AI assistant that serves as the primary interface for the application. It's designed to understand natural language queries and respond with accurate, relevant information.

### 3.1 Two-Tier Cognitive Engine

The core of the AI assistant is a two-tier cognitive engine that's designed to be both fast and intelligent:

*   **Tier 0: Simple Responses (`app.py`):** The system first checks for simple, conversational inputs like "thanks" or "ok" and provides a canned response. This is fast and avoids unnecessary calls to the AI model.
*   **Tier 1: Intent Recognition (`gemini_integration.py`):** If the input is more complex, the system sends it to the Gemini AI model to determine the user's intent (e.g., `find_owner`, `create_task`).
*   **Tier 2: Tool-Based Routing (`app.py`):** Based on the intent, the system calls the appropriate function to handle the request (e.g., `find_owner()`, `create_task()`).
*   **Tier 3: LLM Escalation (`gemini_integration.py`):** If the intent is unknown, the system escalates the query to the Gemini model for a more general, conversational response.

### 3.2 Data Flow Example: "Who owns Palm Tower Unit 3401?"

1.  The user types "who owns palm tower unit 3401?" into the chat interface and clicks "send."
2.  The frontend sends a POST request to the `/api/chat` endpoint in `app.py`.
3.  The `chat()` function calls the `route_command()` function to process the message.
4.  `route_command()` sends the message to the `get_intent()` function in `gemini_integration.py`.
5.  The Gemini model returns the intent `find_owner`.
6.  `route_command()` calls the `find_owner()` function in `app.py`.
7.  `find_owner()` calls the `find_properties_in_text()` function in `knowledge_base.py` to identify the property.
8.  `find_owner()` then queries the database (via `database.py`) to find the owner of the property.
9.  The owner's information is returned to the frontend and displayed in the chat interface.

## 2. Automation and Analytics (`automation.py` and `analytics.py`)

These modules contain the business logic for the application's more advanced features.

### 2.1 Automation (`automation.py`)

This module contains functions for automating common tasks.

#### `get_follow_up_tasks()`

This function generates a prioritized list of follow-up tasks based on the lead status and last contact date of your contacts.

*   **Algorithm:**
    1.  The function defines a set of follow-up intervals for each lead status (e.g., 1 day for "Hot" leads, 3 days for "Warm" leads).
    2.  It then queries the database for all contacts that haven't been contacted within their specified interval.
    3.  For each of these contacts, it calculates a priority score based on their lead status and how overdue the follow-up is.
    4.  Finally, it returns a list of follow-up tasks, sorted by priority.

#### `find_matching_buyers()`

This function finds potential buyers for a given property based on their profile and preferences.

*   **Algorithm:**
    1.  The function first gets the details of the property, including its type, number of bedrooms, and price.
    2.  It then queries the database for all "Hot" and "Warm" leads who are not already property owners.
    3.  For each of these leads, it calculates a match score based on how well their preferences (as indicated in their notes) match the property's details.
    4.  Finally, it returns a list of potential buyers, sorted by their match score.

#### `draft_follow_up_email()`

This function drafts a personalized follow-up email for a contact.

*   **Algorithm:**
    1.  The function gets the contact's information and the appropriate email template from the database.
    2.  It then gets the contact's most recent property interest.
    3.  Finally, it uses this information to personalize the email template and returns the final email.

### 2.2 Analytics (`analytics.py`)

This module contains functions for analyzing your data and providing insights.

#### `score_leads()`

This function scores all of your leads based on a variety of factors.

*   **Algorithm:**
    1.  The function gets all of the contacts from the database.
    2.  For each contact, it calculates a score based on the following factors:
        *   **Lead Status (40% weight):** "Hot" leads get a higher score than "Cold" leads.
        *   **Lead Source (15% weight):** Leads from referrals and previous clients get a higher score than leads from cold calls.
        *   **Recency of Contact (20% weight):** Leads that have been contacted recently get a higher score.
        *   **Engagement Level (15% weight):** Leads that have shown more interest in properties get a higher score.
        *   **Intent Signals (10% weight):** Leads whose notes contain high-intent keywords (e.g., "urgent," "ready to buy") get a higher score.
    3.  The function then returns a list of all leads, sorted by their score.

#### `get_market_insights()`

This function provides real-time insights into the real estate market.

*   **Algorithm:**
    1.  The function queries the database for all available properties in a given area.
    2.  It then calculates a variety of market statistics, including the average price, the number of properties on the market, and the most common property type.
    3.  Finally, it returns a dictionary of market insights.

#### `get_performance_metrics()`

This function provides a detailed overview of your performance.

*   **Algorithm:**
    1.  The function queries the database for all of your deals, contacts, and tasks.
    2.  It then calculates a variety of performance metrics, including your conversion rate, average deal size, and task completion rate.
    3.  Finally, it returns a dictionary of performance metrics.

#### `predict_deal_probability()`

This function predicts the probability of a deal closing.

*   **Algorithm:**
    1.  The function gets the details of the deal, including the lead's score, the property's price, and the age of the deal.
    2.  It then calculates a probability score based on a simple algorithm that takes into account the lead's status, the lead's source, the age of the deal, and how recently the lead was contacted.
    3.  Finally, it returns a dictionary that includes the probability of the deal closing, a breakdown of the probability factors, and a set of recommendations for improving the probability.
