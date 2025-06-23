# Aigile Module 1: AI-Powered User Story and Acceptance Criteria Generation

## 🚀 Overview

Module 1 is the foundational component of the **Aigile** project - an AI-powered Scrum automation platform that revolutionizes agile development workflows. This module automates the transformation of natural language project requirements into structured, prioritized user stories with comprehensive acceptance criteria, seamlessly integrated into Jira workspaces.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Components](#-components)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Technical Implementation](#-technical-implementation)
- [Development](#-development)
- [License](#-license)

## ✨ Features

### 🎯 Core Capabilities

- **🤖 AI-Powered Story Generation**: Transforms natural language requirements into structured user stories using advanced language models
- **📊 Intelligent Prioritization**: Multi-agent evaluation system with dollar allocation methodology for priority assignment
- **✅ Acceptance Criteria Creation**: Generates comprehensive, testable acceptance criteria using multi-stakeholder perspectives
- **🔗 Jira Integration**: Seamless integration with Atlassian Jira for direct backlog management
- **⚡ Asynchronous Processing**: Job-based architecture for handling long-running AI operations
- **🎨 Professional UI**: Modern, responsive interface built with Atlassian Design System

### 🔧 Advanced Features

- **🔄 Never-Give-Up Polling**: Continuous status monitoring for long-running operations
- **📝 Permanent Story Numbering**: Stable story identifiers that persist across operations
- **🎛️ Batch Operations**: "Add All to Backlog" functionality with error handling
- **🧠 Multi-Agent AI System**: Product Owner, Senior Developer, and QA perspectives
- **🔍 Similarity Filtering**: Removes duplicate acceptance criteria using semantic analysis
- **🛡️ Robust Error Handling**: Comprehensive error recovery and user feedback

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Module 1 Architecture                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Atlassian Forge Apps)                          │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │ User Story App  │  │ Acceptance Criteria App         │   │
│  │ - React UI      │  │ - React UI                      │   │
│  │ - Job Management│  │ - Individual AC Generation      │   │
│  │ - Batch Ops     │  │ - Storage Management            │   │
│  └─────────────────┘  └─────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Backend Services (Python Flask)                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ AI Processing Pipeline                                  │ │
│  │ - Story Generation (generate_us.py)                    │ │
│  │ - Prioritization (prioritize_us.py)                    │ │
│  │ - AC Generation (generate_ac.py)                       │ │
│  │ - Text Processing & Validation                         │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  External Services                                          │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │ Groq AI API     │  │ Atlassian Jira                  │   │
│  │ - LLaMA Models  │  │ - Issue Management              │   │
│  │ - Rate Limiting │  │ - Project Integration           │   │
│  └─────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Components

### 📱 Frontend Applications

#### 1. User Story Generator App (`user_story_app/`)
- **Primary Interface**: Requirements input and story generation
- **Technology**: React + Atlassian Forge
- **Key Features**:
  - Natural language requirements input with validation
  - Real-time progress tracking with elapsed time
  - Permanent story numbering system
  - Individual and batch Jira integration
  - Job-based asynchronous processing

#### 2. Acceptance Criteria App (`acceptance_criteria/`)
- **Purpose**: Individual story AC generation
- **Technology**: React + Atlassian Forge
- **Key Features**:
  - Single story AC generation
  - Issue-specific storage isolation
  - Similarity-based filtering
  - Direct Jira issue integration

### 🐍 Backend Services (`python scripts/`)

#### Core Processing Pipeline
- **`main/pipeline_1_generate_user_stories.py`**: Flask API service with asyncio support
- **`helpers/generate_us.py`**: User story generation with AI integration
- **`helpers/prioritize_us.py`**: Multi-agent prioritization system
- **`helpers/generate_ac.py`**: Acceptance criteria generation with CUU methodology

#### AI Prompt Engineering
- **`Instructions/`**: System prompts, role definitions, and output formats
- **`Examples/`**: Few-shot learning examples for consistent AI responses
- **Multi-role perspectives**: Product Owner, Senior Developer, QA, and Others

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Atlassian Forge CLI
- Jira Cloud instance

### 1. Clone Repository
```bash
git clone https://github.com/your-org/Module1-Backlog-Generation.git
cd Module1-Backlog-Generation
```

### 2. Setup Python Backend
```bash
cd "python scripts"
pip install -r requirements.txt

# Set up environment variables
export GROQ_API_KEY="your_groq_api_key"

# Run the Flask service
python main/pipeline_1_generate_user_stories.py
```

### 3. Deploy User Story App
```bash
cd user_story_app
npm install
forge deploy

# Install in your Jira instance
forge install
```

### 4. Deploy Acceptance Criteria App
```bash
cd acceptance_criteria
npm install
forge deploy
forge install
```

## 📖 Usage

### 1. User Story Generation

1. **Navigate** to any Jira issue
2. **Open** the User Story Generator panel
3. **Enter** project requirements in natural language
4. **Click** "Generate Stories" 
5. **Monitor** progress with real-time updates
6. **Review** generated stories with priorities
7. **Add** individual stories or use "Add All to Backlog"

### 2. Acceptance Criteria Generation

1. **Open** any Jira issue with a user story
2. **Access** the Acceptance Criteria panel
3. **Click** "Generate Acceptance Criteria"
4. **Review** multi-perspective criteria
5. **Edit** or approve generated criteria

## 🔌 API Documentation

### User Story Generation API

```http
POST https://your-service.pythonanywhere.com/generate_and_priortize_us
Content-Type: application/json

{
  "body": "Project requirements in natural language"
}
```

**Response:**
```json
{
  "result": [
    {
      "key": "US001",
      "user_story": "As a user, I want to...",
      "epic": "Epic Name",
      "description": "Detailed description",
      "ranking": 1
    }
  ]
}
```

### Acceptance Criteria API

```http
POST https://your-service.pythonanywhere.com/generate-single-ac
Content-Type: application/json

{
  "body": "User story title and description"
}
```

**Response:**
```json
{
  "result": [
    "Given [context], when [action], then [outcome]",
    "Acceptance criterion 2...",
    "Acceptance criterion 3..."
  ]
}
```

## 🔬 Technical Implementation

### Multi-Agent Prioritization System

The system employs three specialized AI agents for comprehensive story evaluation:

1. **Product Owner Agent**: Business value and market impact assessment
2. **Senior Developer Agent**: Technical complexity and feasibility analysis  
3. **QA Agent**: Testability verification and edge case coverage

**Dollar Allocation Algorithm:**
```
Input: Stories S₁, S₂, ..., Sₙ with allocations A₁, A₂, ..., Aₙ where ΣAᵢ = 100
Process: Sort by allocation (descending) → Map positions to priority levels
Output: Balanced priority distribution across all five Jira priority levels
```

### CUU (Create-Update-Update) Methodology

Acceptance criteria generation follows a three-stage refinement process:

1. **Create**: Product Owner/Business Analyst perspective
2. **Update 1**: Quality Analyst enhancements
3. **Update 2**: Other team members' additions

### Asynchronous Job Architecture

```javascript
// Job lifecycle with persistent polling
CREATED → PROCESSING → COMPLETED / FAILED

// Never-give-up polling implementation
const pollJobStatus = async (jobId) => {
  const status = await checkStatus(jobId);
  if (!status.completed) {
    setTimeout(() => pollJobStatus(jobId), 2000);
  }
};
```

### Data Security & Privacy

- **Temporary Storage**: 24-hour automatic data expiration
- **Context Isolation**: Issue-specific data namespacing
- **API Security**: Rate limiting and key rotation
- **Privacy**: No permanent storage of business data

## 🛠️ Development

### Project Structure
```
Module1-Backlog-Generation/
├── user_story_app/              # Main story generation app
│   ├── src/
│   │   ├── frontend/           # React components
│   │   └── resolvers/          # Backend API resolvers
│   └── manifest.yml            # Forge app configuration
├── acceptance_criteria/         # AC generation app
│   ├── src/
│   │   ├── frontend/           # React components
│   │   └── resolvers/          # Backend API resolvers
│   └── manifest.yml
├── python scripts/             # AI processing backend
│   ├── main/                   # Flask API services
│   ├── helpers/                # Core AI functions
│   ├── Instructions/           # Prompt templates
│   └── Examples/               # Training examples
└── Module1_Documentation.md    # Technical documentation
```

### Key Technologies

- **Frontend**: React, Atlassian Forge, Atlassian Design System
- **Backend**: Python Flask, asyncio, scikit-learn
- **AI**: Groq API with LLaMA 3 models
- **Storage**: Atlassian Forge Storage API
- **Integration**: Jira REST API

### Development Commands

```bash
# Watch mode for frontend development
forge tunnel

# View application logs
forge logs

# Deploy changes
forge deploy

# Install in development instance
forge install --upgrade
```

## 📊 Performance Metrics

- **Story Generation**: 30 seconds - 3 minutes (depending on complexity)
- **AC Generation**: 15-45 seconds per story
- **Memory Usage**: <512MB per Forge function
- **Storage**: Automatic cleanup after 24 hours
- **Reliability**: Multi-key API rotation for 99%+ uptime

## 🧪 Quality Assurance

### Multi-Layer Validation
1. **Input Sanitization**: Text preprocessing and validation
2. **AI Response Validation**: JSON structure and completeness checking
3. **Business Logic Validation**: Story format and epic consistency
4. **Integration Validation**: Jira compatibility verification

### Error Handling
- **Network Failures**: Exponential backoff retry (1s, 2s, 4s intervals)
- **AI Service Timeouts**: Graceful degradation with user notification
- **Partial Failures**: Individual story error isolation
- **User Communication**: Clear error messages with recovery guidance

## 🔄 Future Roadmap

- [ ] Sprint planning automation
- [ ] Story estimation integration
- [ ] Advanced epic management
- [ ] Team velocity analytics
- [ ] Multi-project support
- [ ] Custom prompt templates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of the Aigile platform. All rights reserved.

---

**Module 1** is the foundation of intelligent agile automation. By combining advanced AI with seamless Jira integration, it transforms how development teams approach backlog creation and management.

For technical details, see [Module1_Documentation.md](./Module1_Documentation.md)
