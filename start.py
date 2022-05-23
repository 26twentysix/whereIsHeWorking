from src.app import core

import os

if __name__ == '__main__':
    app = core.App()
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    app.set_access_token(dotenv_path)
    app.run_app()
