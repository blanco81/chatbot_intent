from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.apiv1.chat import router as chat_router



app = FastAPI()

app.include_router(chat_router, prefix="/core", tags=["Chat"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the frontend directory
app.mount("/core/frontend", StaticFiles(directory="frontend"), name="frontend")



