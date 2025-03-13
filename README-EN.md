[简体中文](README.md) | English

## 📚 Detailed Features

### 🤖 Intelligent AI Conversation

- **Multi-turn Interaction**: Natural and smooth multi-turn conversation experience for deeper communication and exploration.
- **Real-time Streaming Response**: Say goodbye to long waits with real-time AI responses for more efficient conversations.
- **History Management**: Convenient viewing and management of conversation history, review brilliant dialogues anytime.
- **Web Search**: Integrated web search functionality allows AI to access internet information for more comprehensive and timely answers.
- **Code Rendering**: Intelligent recognition and rendering of code blocks for an enhanced code reading experience.

### 📄 Intelligent Document Conversation

- **Multi-format Document Support**: Support for uploading and parsing PDF, DOC, PPT, TXT, and other document formats.
- **Deep Document Understanding**: AI can understand document content and structure for deeper interactive conversations.
- **Contextual Relevance**: Context-related conversations based on document content to answer your specific questions.
- **Document Content Retrieval**: Quickly retrieve key information within documents to improve information acquisition efficiency.

### 🖼️ Multimodal Image Recognition

- **Multiple Image Formats**: Support for common image formats such as JPG, PNG, JPEG.
- **Intelligent Scene Recognition**: Using multimodal models to accurately identify scenes and objects in images.
- **OCR Text Extraction**: Powerful OCR functionality to quickly extract text information from images.
- **Multi-turn Image-based Dialogue**: Engage in multi-turn in-depth conversations about image content to explore the stories behind the images.

### 📝 Flexible Prompt Management

- **Built-in Prompt Templates**: Curated common prompt templates for quick start and inspiration.
- **Custom Prompts**: Freely create and edit prompts to meet your personalized needs.
- **Category Management**: Categorize prompts for easy finding and use.
- **One-click Application**: Quickly apply prompts to simplify operation processes.

### 🗂️ Powerful Model Library

- **Multi-model Management**: Centrally manage various models installed in Ollama.
- **Model Information Display**: Clearly display model names, sizes, and other information.
- **Quick Model Switching**: Switch the current model with one click to experience different model characteristics.
- **Model Library Expansion**: Support for pulling GGUF and safetensors models from Hugging Face and Ollama to expand your model library.

### 🌍 Multilingual Support

- **Interface Language Switching**: Support for Chinese, English, and other language interfaces to meet the needs of different users.
- **Language Setting Persistence**: Language preferences are saved and automatically applied on your next visit.
- **Global Translation**: All text elements in the application support multilingual display, including buttons, prompts, labels, etc.

## 🔮 Future Plans (Roadmap)

- **Agent Functionality**: Implement a more intelligent Agent system to handle complex tasks.
- **Tool Calling**: Support for calling external tools and services to extend AI capabilities.
- **Voice Conversation**: Add speech recognition and synthesis for voice interaction.

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
3. Begin chatting happily with your model!

## 3. Custom Models (Modelfile)

### Steps:
1. Go to the "Model Library" page
2. Click the "Custom" button
3. Enter a model name (Chinese supported)
4. Select a base model
5. Enter system prompts (to define roles or behaviors)
6. Click create to complete customization

### Tips:
- If the prompt defines a role, the new model will converse with you in that role

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

> Note: kun-lab is still in rapid iterative development, your contributions and feedback are crucial to us!
