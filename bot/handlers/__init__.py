from bot.handlers.start import router as start_router
from bot.handlers.channels import router as channels_router
from bot.handlers.creatives import router as creatives_router
from bot.handlers.pool import router as pool_router
from bot.handlers.deals import router as deals_router
from bot.handlers.join_requests import router as join_requests_router
from bot.handlers.leads import router as leads_router
from bot.handlers.broadcast import router as broadcast_router
from bot.handlers.admin import router as admin_router

__all__ = [
    "start_router",
    "channels_router",
    "creatives_router",
    "pool_router",
    "deals_router",
    "join_requests_router",
    "leads_router",
    "broadcast_router",
    "admin_router",
]
