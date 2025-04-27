<div align="center">

<a href="https://kunpuai.com/"><img src="./frontend/src/assets/kunlab_bg_logo.svg" width="120" height="120" alt="kun-lab logo"></a>

# kun-lab

<p align="center">
  <a href="./README-EN.md">English</a> |
  <a href="./README.md">简体中文</a>
</p>

[![Version](https://img.shields.io/github/v/release/bahamutww/kun-lab?color=blue&include_prereleases&label=Version)](https://github.com/bahamutww/kun-lab/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Windows Support](https://img.shields.io/badge/Windows-Supported-blue.svg)](https://github.com/bahamutww/kun-lab/releases)

</div>

# kun-lab

**Your Local Intelligent Conversation Partner**

kun-lab is a lightweight AI conversation application based on Ollama, designed to provide you with a simple, efficient, and feature-rich local AI conversation experience. With no complicated configuration required, it's ready to use out of the box, allowing you to easily enjoy powerful AI capabilities while keeping all your data under local control, ensuring your privacy and security.

## 📑 Table of Contents

- [✨ Core Highlights](#-core-highlights)
- [📷 Application Screenshots](#-application-screenshots)
- [🚀 Quick Start](#-quick-start)
- [📚 Usage Guide](#-usage-guide)
- [🔧 Feature Details](#-feature-details)
- [🛠️ Technology Stack](#️-technology-stack)
- [📞 Contact Us](#-contact-us)

## 📷 Application Screenshots

<div align="center">
  <img src="./frontend/src/assets/home_page.jpg" width="80%" alt="Home Page">
  <p align="center"><em>Home Page - Empty state without favorited models</em></p>
</div>

<div align="center">
  <img src="./frontend/src/assets/homemodel_page.jpg" width="80%" alt="Home Page with Models">
  <p align="center"><em>Home Page - Favorited models displayed on the home page</em></p>
</div>

<div align="center">
  <img src="./frontend/src/assets/chat_page.jpg" width="80%" alt="Chat Interface">
  <p align="center"><em>Chat Interface - Smooth conversation experience with rich feature support</em></p>
</div>

<div align="center">
  <img src="./frontend/src/assets/model_page.jpg" width="80%" alt="Model Management Interface">
  <p align="center"><em>Model Management - Easily manage and use various AI models</em></p>
</div>

<div align="center">
  <img src="./frontend/src/assets/modeldetails_page.jpg" width="80%" alt="Model Details Interface">
  <p align="center"><em>Model Details - Detailed information of local models</em></p>
</div>

<div align="center">
  <img src="./frontend/src/assets/custom_page.jpg" width="80%" alt="Custom Model Interface">
  <p align="center"><em>Custom Model - Model customization gives you more control to play various roles</em></p>
</div>

## ✨ Core Highlights

- **🚀 Flexible Multi-model Switching**: Easily manage and select various models supported by Ollama to meet your different conversation needs.
- **💬 Ultra-fast Streaming Dialogue**: Experience smooth real-time conversations with instant AI responses.
- **📄 Intelligent Document Parsing**: Support for PDF, DOC, PPT, TXT and other document formats, quickly understanding document content and answering your questions.
- **🖼️ Multimodal Image Understanding**: Support for multimodal models that not only recognize images but also understand the scenes and intentions behind them, supporting multi-turn conversations based on images.
- **🌐 Web Search Enhancement**: Integrated web search capabilities give AI a broader knowledge base, with deep search available for more complex questions as needed.
- **💻 Code Rendering**: Automatic code block rendering supports multiple programming languages, making code display clearer and easier to understand.
- **🗂️ Model Library Extension**: Support for pulling open-source models from Hugging Face and Ollama, GGUF and safetensors model formats, for more flexible model management.
- **📝 Prompt Templates**: Built-in rich prompt templates, with support for custom and categorized management, easily inspiring AI creativity.
- **🔒 Local Data Storage**: All data is stored locally, focusing on user privacy, secure and reliable.
- **🌍 Multilingual Support**: Support for Chinese, English and other language interfaces to meet the needs of different users.
- **👥 Multi-user Concurrent Support**: Support for multiple users to log in independently and be online simultaneously, with each user having their own conversation space and personalized settings, meeting the needs of families, small teams or organizations for shared use, improving resource utilization efficiency.
- **✍️ Quick Note Feature**: Supports Markdown syntax, provides real-time preview, and enables one-click export, making knowledge organization more efficient.


## 🚀 Quick Start

### Desktop Application Installation (Recommended)

1. **Download the Installation Package**:
   - Visit the [Release Page](https://github.com/bahamutww/kun-lab/releases) to download the installation package for your platform
   - Windows: `.exe` installer (currently only Windows is supported)
   - macOS: `.dmg` package
   - Linux: `.AppImage` or `.deb` package

2. **Install and Run**:
   - Double-click the installation package and follow the prompts to complete the installation
   - After installation, you can run it directly without any additional configuration

## 📚 Usage Guide

#### Environment Requirements

- **Operating System**: Windows/macOS/Linux (Windows recommended)
- **Python**: 3.10+
- **Node.js**: 20.16.0+
- **Ollama Service**: Ensure Ollama service is properly installed and running

#### Installation Steps

1. **Get the Code**:

   ```bash
   git clone https://github.com/bahamutww/kun-lab.git
   cd kun-lab
   ```

2. **Virtual Environment Setup**:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Configure backend environment**:

   ```bash
   cd backend
   python setup.py or pip install -r requirements.txt
   ```

4. **Configure frontend environment**:

   ```bash
   cd frontend
   npm install
   ```

5. **Environment variable configuration**:

   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   # Modify the configuration items in the .env file according to your actual situation
   ```

6. **Start kun-lab**:

   ```bash
   # Run in the project root directory (after installing backend dependencies)
   python run_dev.py
   ```

7. Open your browser and visit http://localhost:5173 to start experiencing kun-lab!


## 🔧 Feature Details

### 🤖 Intelligent AI Conversation

- **Multi-turn Interaction**: Natural and smooth multi-turn conversation experience for deeper communication and exploration.
- **Real-time Streaming Response**: Say goodbye to long waits, AI responses appear in real-time for more efficient conversations.
- **History Management**: Convenient viewing and management of conversation history, review brilliant conversations anytime.
- **Web Search**: Integrated web search functionality allows AI to access internet information, providing more comprehensive and timely answers.
- **Code Rendering**: Intelligent recognition and rendering of code blocks, enhancing code reading experience.

### 📄 Intelligent Document Conversation

- **Multi-format Document Support**: Support for uploading and parsing PDF, DOC, PPT, TXT and other document formats.
- **Deep Document Understanding**: AI can understand document content and structure for deeper interactive conversations.
- **Context Association**: Context-relevant conversations based on document content to answer your specific questions.
- **Document Content Retrieval**: Quickly retrieve key information within documents, improving information acquisition efficiency.

### 🖼️ Multimodal Image Recognition

- **Multi-format Images**: Support for common image formats such as JPG, PNG, JPEG.
- **Intelligent Scene Recognition**: Using multimodal models to accurately identify scenes and objects in images.
- **OCR Text Extraction**: Powerful OCR functionality to quickly extract text information from images.
- **Multi-turn Conversations Based on Images**: Engage in deep multi-turn conversations about image content, exploring the stories behind the images.

### 📝 Flexible Prompt Management

- **Built-in Prompt Templates**: Carefully selected common prompt templates for quick start and inspiration.
- **Custom Prompts**: Freely create and edit prompts to meet your personalized needs.
- **Category Management**: Categorize prompts for easy finding and use.
- **One-click Application**: Quickly apply prompts, simplifying the operation process.

### 🗂️ Powerful Model Library

- **Multi-model Management**: Centrally manage various models installed in Ollama.
- **Model Information Display**: Clearly display model name, size and other information.
- **Quick Model Switching**: Switch the current model with one click to experience different model characteristics.
- **Model Library Extension**: Support for pulling GGUF and safetensors models from Hugging Face and Ollama to expand your model library.

### 🌍 Multilingual Support

- **Interface Language Switching**: Support for Chinese, English and other language interfaces to meet the needs of different users.
- **Language Setting Persistence**: Language preferences are saved and automatically applied on your next visit.
- **Global Translation**: All text elements in the application support multilingual display, including buttons, prompts, labels, etc.

### ✍️ Quick Note Feature

- **Markdown Support**: Full support for Markdown syntax, including headings, lists, code blocks, tables, and more.
- **Real-time Preview**: Preview rendering effects in real-time while editing, what you see is what you get.
- **One-click Export**: Support for exporting to MD format, making it convenient to share and archive your notes.

## 🔮 Future Plans (Roadmap)

- **Agent Functionality**: Implement a smarter Agent system to handle complex tasks.
- **Tool Calling Functionality**: Support for calling external tools and services to extend AI capabilities.
- **Voice Conversation Functionality**: Add speech recognition and synthesis for voice interaction.

## 🛠️ Technology Stack

### Backend

- **FastAPI**: Building high-performance API services
- **WebSocket**: Implementing real-time two-way communication
- **JWT Authentication**: Ensuring API security
- **PDF Processing**: Powerful PDF document parsing capabilities
- **OCR Engine**: Efficient text recognition engine

### Frontend

- **Vue 3**: Building interactive user interfaces
- **TypeScript**: Enhancing code maintainability
- **WebSocket**: Supporting real-time communication
- **Internationalization Framework**: Providing multilingual support

## 📂 Directory Structure

```
kun-lab/
├── backend/             # Backend code
│   ├── api/             # API interfaces
│   ├── core/            # Core functional modules
│   └── data/            # Data storage related
├── frontend/            # Frontend code
│   ├── src/             # Source code
│   │   ├── i18n/        # Internationalization related
│   │   ├── api/         # API client
│   │   └── components/  # UI components
│   └── public/          # Static resources
└── run_dev.py           # Development server startup script
```

## 🧑‍💻 Development Guide

### Starting Development Mode

```bash
# Start complete development server (frontend + backend)
python run_dev.py

# Start backend service only
cd backend
python main.py

# Start frontend service only
cd frontend
npm run dev
```

## kun-lab Operation Guide

## 1. Pulling Models

### Steps:
1. Go to the "Model Library" page
2. Click the "Pull Model" button
3. Enter `ollama run + model name` in the input box, then confirm to start pulling

### Tips:
- You can check model names on the [Ollama Official Model List](https://ollama.com/library), for example: `ollama run qwq:32b`
- Also supports GGUF format models on Hugging Face, input format is `ollama run hf.co/account/model name`, for example: `ollama run hf.co/Qwen/QwQ-32B-GGUF:Q2_K`

## 2. Chat Conversation

### Steps:
1. Go to the "Chat Conversation" page
2. Start by any of the following methods:
   - Click "New Conversation" in the side navigation bar
   - Click the "Start New Conversation" button on the home page
   - Select a specific model and click "Start New Conversation"
3. Start chatting happily with your model!

## 3. Custom Model (Modelfile)

### Steps:
1. Go to the "Model Library" page
2. Click the "Custom" button
3. Enter a model name (Chinese supported)
4. Select a base model
5. Enter system prompts (used to define roles or behaviors)
6. Click create to complete customization

### Tips:
- If the prompt defines a role, the new model will converse with you as that role


## 🤝 Contributing

We warmly welcome your contributions to the kun-lab project!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your code changes (`git commit -am 'Add some feature'`)
4. Push the branch (`git push origin feature/your-feature`)
5. Create a Pull Request

## 📜 License

Apache 2.0 License

## 🔗 More Resources

- Project Documentation: `docs/`
- Changelog: `CHANGELOG.md`
- Issue Feedback: `issues`

## 🙏 Special Thanks

- [Ollama](https://ollama.ai/): Powerful local model running framework
- [FastAPI](https://fastapi.tiangolo.com/): Modern Web API framework
- [Vue](https://vuejs.org/): Popular JavaScript UI library

## 📞 Contact Us

If you have any questions or suggestions, please feel free to contact us through:

- Submit an Issue: Submit your questions or suggestions on the GitHub repository issues page.

- Email: [service@kunpuai.com](service@kunpuai.com)

> Friendly reminder: kun-lab is still in rapid iterative development, your contributions and feedback are crucial to us!

