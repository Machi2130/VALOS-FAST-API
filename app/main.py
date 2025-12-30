# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.responses import JSONResponse
# from contextlib import asynccontextmanager
# import os

# from app.routes import auth_router, sales_router, costing_router, quotation_router
# from app.config import get_settings
# from app.database import create_db_and_tables

# settings = get_settings()


# # Lifespan event handler (startup/shutdown)
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: Create tables in Neon DB
#     print("🚀 Starting FastAPI application...")
#     print("📊 Creating database tables in Neon DB...")
#     try:
#         await create_db_and_tables()
#         print("✅ Database tables created successfully!")
#     except Exception as e:
#         print(f"⚠️  Error creating tables: {e}")
#         print("   Tables may already exist, continuing...")
    
#     print(f"🌐 Environment: {'Development' if settings.debug else 'Production'}")
#     yield
#     # Shutdown
#     print("👋 Shutting down FastAPI application...")


# # Create FastAPI app
# app = FastAPI(
#     title="Sales & Costing Management API",
#     description="FastAPI backend for sales CRM, costing calculator, and quotation management",
#     version="1.0.0",
#     docs_url="/docs" if settings.debug else None,  # Disable docs in production
#     redoc_url="/redoc" if settings.debug else None,
#     lifespan=lifespan
# )

# # CORS Configuration for Netlify Frontend + Render Backend
# allowed_origins = [
#      "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:3000",           # Local React dev
#     "http://localhost:5173",           # Local Vite dev
#     "http://localhost:8000",           # Local FastAPI
#     "https://*.netlify.app",           # Netlify preview deployments
#     "https://your-app.netlify.app",    # Replace with your Netlify domain
#     # Add your custom domain if you have one
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins,          # ❌ not ["*"]
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Get additional origins from environment variable
# if os.getenv("FRONTEND_URL"):
#     allowed_origins.append(os.getenv("FRONTEND_URL"))

# # In production, be more restrictive
# if not settings.debug:
#     # Remove localhost origins in production
#     allowed_origins = [origin for origin in allowed_origins if not origin.startswith("http://localhost")]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins if not settings.debug else ["*"],  # Allow all in dev
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
#     expose_headers=["*"],
#     max_age=3600,  # Cache preflight requests for 1 hour
# )

# # Trusted Host Middleware (security)
# if not settings.debug:
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=[
#             "*.onrender.com",              # Render domains
#             "your-app.onrender.com",       # Replace with your Render domain
#             "*.netlify.app",               # Netlify domains
#         ]
#     )

# # Include routers
# app.include_router(auth_router)
# app.include_router(sales_router)
# app.include_router(costing_router)
# app.include_router(quotation_router)


# # Root endpoint
# @app.get("/")
# async def root():
#     return {
#         "message": "Sales & Costing Management API",
#         "version": "1.0.0",
#         "status": "running",
#         "environment": "production" if not settings.debug else "development",
#         "docs": "/docs" if settings.debug else "Disabled in production"
#     }


# # Health check endpoint (required by Render)
# @app.get("/health")
# async def health_check():
#     """Health check endpoint for Render monitoring"""
#     return {
#         "status": "healthy",
#         "database": "connected"
#     }


# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=500,
#         content={
#             "detail": "Internal server error",
#             "error": str(exc) if settings.debug else "An error occurred"
#         }
#     )


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=int(os.getenv("PORT", 8000)),
#         reload=settings.debug
#     )
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import time

from app.routes import auth_router, sales_router, costing_router, quotation_router
from app.config import get_settings
from app.database import create_db_and_tables, engine

settings = get_settings()

# ─────────────────────────────────────────────
# Lifespan (startup / shutdown)
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting FastAPI application...")
    print("📊 Creating database tables...")

    try:
        await create_db_and_tables()
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️ DB init warning: {e}")

    print(f"🌐 Environment: {'Development' if settings.debug else 'Production'}")
    yield
    print("👋 Shutting down FastAPI application...")
    await engine.dispose()


# ─────────────────────────────────────────────
# Create FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title="Sales & Costing Management API",
    description="Backend for CRM, costing & quotations",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ─────────────────────────────────────────────
# ✅ CORS — SINGLE, CORRECT CONFIG
# ─────────────────────────────────────────────
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "friendly-douhua-0f34ab.netlify.app",
]

# Optional prod frontend (Netlify / custom)
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Trusted Hosts (ONLY in production)
# ─────────────────────────────────────────────
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "*.onrender.com",
            "*.netlify.app",
        ],
    )

# ─────────────────────────────────────────────
# Request Timing Middleware (DEBUG only)
# ─────────────────────────────────────────────
if settings.debug:
    @app.middleware("http")
    async def log_request_timing(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start_time) * 1000
        
        # Color code based on response time
        if elapsed < 100:
            color = "\033[92m"  # Green
        elif elapsed < 500:
            color = "\033[93m"  # Yellow
        else:
            color = "\033[91m"  # Red
        reset = "\033[0m"
        
        print(f"{color}[{elapsed:.2f}ms]{reset} {request.method} {request.url.path}")
        return response


# ─────────────────────────────────────────────
# Include Routers
# ─────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(sales_router)
app.include_router(costing_router)
app.include_router(quotation_router)

# ─────────────────────────────────────────────
# Root
# ─────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Sales & Costing Management API",
        "status": "running",
        "environment": "development" if settings.debug else "production",
    }

# ─────────────────────────────────────────────
# Health check (Render / monitoring)
# ─────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ─────────────────────────────────────────────
# Global Exception Handler
# ─────────────────────────────────────────────
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=500,
#         content={
#             "detail": "Internal server error",
#             "error": str(exc) if settings.debug else "Something went wrong",
#         },
#     )

# ─────────────────────────────────────────────
# Local run support
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.debug,
    )
