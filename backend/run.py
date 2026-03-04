from app import create_app
import uvicorn

# Crée l'application en utilisant la factory
app, asgi_app = create_app()

if __name__ == "__main__":
    print("Script started")
    print("Script finished")
    uvicorn.run("run:asgi_app", host='127.0.0.1', port=8000, reload=True, log_level="info")

