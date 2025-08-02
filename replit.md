# Digital Twin - AI-Powered Real Estate Command Center

## Overview

Digital Twin is a comprehensive real estate management platform that combines AI-powered assistance with traditional CRM capabilities. The system features AURA, an intelligent assistant powered by Google's Gemini AI, which provides natural language interaction for property management, lead scoring, task automation, and market analysis. The platform serves as a command center for real estate professionals, integrating property data, contact management, deal tracking, and analytics in a unified interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Single-page application built with Vue.js 3
- **Styling**: Tailwind CSS for responsive design and consistent theming
- **UI Components**: Font Awesome icons, Chart.js for data visualization
- **Layout**: Modular tab-based interface with sidebar navigation
- **State Management**: Vue's reactive data system for real-time updates

### Backend Architecture
- **Framework**: Flask web server with Python
- **API Design**: RESTful endpoints for chat, file uploads, and data management
- **Modular Structure**: Separated concerns across multiple modules:
  - `app.py`: Main Flask application and routing
  - `automation.py`: Task automation and follow-up management
  - `analytics.py`: Lead scoring and performance metrics
  - `knowledge_base.py`: Document processing and entity recognition
  - `gemini_integration.py`: AI model interactions
  - `models.py`: Data structures and utilities

### Data Storage
- **Primary Database**: SQLite with structured schema design
- **Core Tables**: Properties, Contacts, Deals, Tasks for operational data
- **Intelligence Tables**: HistoricalTransactions, MasterOwners, KnowledgeNexus for advanced features
- **Relationship Management**: Junction tables for many-to-many relationships (ContactProperties)
- **Embedded Data**: Support for vector embeddings in KnowledgeNexus table for semantic search

### AI Integration
- **Primary AI**: Google Gemini 2.5 Flash for natural language processing
- **Two-Tier Processing**: Keyword-based tool routing followed by LLM escalation
- **Specialized Tools**: Property lookup, task creation, lead scoring, buyer matching
- **Context Management**: Knowledge base integration for relevant information retrieval

### Automation Features
- **Lead Scoring**: Multi-factor analysis with priority categorization
- **Follow-up Management**: Status-based reminder intervals (Hot: 1 day, Warm: 3 days, Cold: 7 days)
- **Task Generation**: Automated task creation based on contact activity
- **Email Drafting**: Template-based communication generation

## External Dependencies

### AI Services
- **Google Gemini API**: Primary language model for AURA assistant
- **API Configuration**: Environment variable-based API key management

### Frontend Libraries
- **Vue.js 3**: JavaScript framework from CDN
- **Tailwind CSS**: Utility-first CSS framework from CDN
- **Chart.js**: Data visualization library
- **Font Awesome**: Icon library for UI elements

### Python Dependencies
- **Flask**: Web framework and application server
- **google-generativeai**: Google AI SDK for Gemini integration
- **sqlite3**: Built-in database interface
- **Werkzeug**: WSGI utilities and file handling

### File Processing
- **Upload Support**: Multiple file formats (documents, images, spreadsheets)
- **Security**: Filename sanitization and extension validation
- **Storage**: Local filesystem with configurable upload directory

### Development Tools
- **Logging**: Python logging module for debugging and monitoring
- **Environment Variables**: OS-based configuration management
- **Error Handling**: Comprehensive exception handling across modules