import asyncio
import os

from src.app import core

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    core.run_app(dotenv_path)
