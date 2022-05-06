from src.app import core
import os


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    core.set_env_vars(dotenv_path)
    core.start_app()