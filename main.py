import asyncio
from bot import bot, dp

import handlers


async def main():
    print(bot.token)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
