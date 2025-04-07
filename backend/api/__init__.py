from fastapi import APIRouter
from .auth import router as auth_router
from .chat import router as chat_router
from .models import router as models_router
from .tools.image import router as image_router
from .tools.prompts import router as prompts_router
from .tools.doc_format import router as doc_format_router
from .tools.tavily_search import router as tavily_search_router
from .tools.language import router as language_router
from .tools.theme import router as theme_router
from .tools.ollama import router as ollama_router
from .tools.network import router as network_router
from .tools.notes import router as notes_router
from .license import router as license_router
from .changelog import router as changelog_router



api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(models_router, tags=["models"])
api_router.include_router(doc_format_router, prefix="/doc", tags=["document"])
api_router.include_router(image_router, tags=["images"])
api_router.include_router(prompts_router, tags=["prompts"])
api_router.include_router(notes_router, prefix="/notes", tags=["notes"])
api_router.include_router(tavily_search_router, prefix="/tavily", tags=["search"])
api_router.include_router(language_router, prefix="/language", tags=["language"])
api_router.include_router(theme_router, prefix="/theme", tags=["theme"])
api_router.include_router(ollama_router, prefix="/ollama", tags=["ollama"])
api_router.include_router(network_router, prefix="/network", tags=["network"])
api_router.include_router(license_router, tags=["license"])
api_router.include_router(changelog_router, tags=["changelog"])
