import nest_asyncio
import asyncio
from app.bot.__main__ import main

nest_asyncio.apply()  # дозволяє запускати event loop рекурсивно

if __name__ == "__main__":
    asyncio.run(main())
