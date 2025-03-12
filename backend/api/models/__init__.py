from fastapi import APIRouter
from .list import router as list_router
from .detail import router as detail_router
from .favorite import router as favorite_router
from .config import router as config_router
from .pull import router as pull_router
from .custom import router as custom_router
from .import_model import router as import_router

router = APIRouter(prefix="/models")

# 先注册具体路由，再注册带参数的路由
router.include_router(list_router)
router.include_router(detail_router)
router.include_router(favorite_router)
router.include_router(config_router)
router.include_router(pull_router)
router.include_router(custom_router)
router.include_router(import_router)
