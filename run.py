from app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    print(f"\n DNA Secure Vault running at http://{Config.HOST}:{Config.PORT}\n")
    app.run(host=Config.HOST, port=Config.PORT, debug=True)
