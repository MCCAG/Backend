from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Config import CORS_ORIGIN
from Scripts.Lifespan import lifespan
from Scripts.Routers import generate_router

app = FastAPI(lifespan=lifespan)
app.include_router(generate_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_origins=CORS_ORIGIN
)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('Main:app', host='0.0.0.0', port=8080, reload=True)
