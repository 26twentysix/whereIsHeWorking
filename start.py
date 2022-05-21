from src.app import core
import os


if __name__ == '__main__':
    list = [1, 2, 3, 4, 5]
    print(str(list))
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    core.set_env_vars(dotenv_path)
    core.run_app()