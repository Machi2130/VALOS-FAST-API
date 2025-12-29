from app.routes.auth import router as auth_router
from app.routes.sales import router as sales_router
from app.routes.costing import router as costing_router
from app.routes.quotation import router as quotation_router

__all__ = ["auth_router", "sales_router", "costing_router", "quotation_router"]
