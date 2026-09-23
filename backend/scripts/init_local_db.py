"""Create an isolated SQLite database with the mobile app's material catalog."""
import asyncio
from src.core.bootstrap import bootstrap_database
from src.core.database import engine


async def main() -> None:
    await bootstrap_database()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
