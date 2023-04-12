discord.bot
==========

This library is a powerful tool for creating custom bots for your Discord community

Welcome to my Discord bot creation library using API 10!

This library is a powerful tool for creating custom bots for your Discord community. API 10 is one of the older versions of the Discord API and is still used by many developers to create bots. With this library, you can create and customize bots with ease and efficiency.

The library is written in a modern and easy-to-learn programming language, allowing anyone with basic programming knowledge to create Discord bots. Additionally, the documentation is clear and comprehensive, providing helpful and detailed examples to help you get started quickly.

Some of the features of this library include:

Custom commands: create your own custom commands to perform specific actions on Discord. API integration: use the Discord API to fetch information about users, channels, and servers. Event management: manage events such as when a user joins a voice channel or sends a message on the server. Automated messages: create automated messages for your users at regular intervals or in response to certain events. This library is an excellent and reliable choice for anyone looking to create bots for Discord using API 10. With clear documentation and helpful examples, you can create custom bots to meet the unique needs of your Discord community.

Please note that this library is currently under development and may be subject to changes and updates. We appreciate your patience and feedback as we work to improve and enhance its features and functionality.

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.

Installing
----------

**Python 3.9 or higher is required**

To install the library you can just run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install git+https://github.com/BosonsHiggs/discord.bot

    # Windows
    py -3 -m pip install git+https://github.com/BosonsHiggs/discord.bot


To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/BosonsHiggs/discord.bot
    $ cd discord.bot


Quick Example
--------------

.. code:: py

    import asyncio
    from discord.bot import ClientApp

    TOKEN = 'BOT TOKEN HERE'
    GUILD_ID = guild_id_here
    aplication_id = aplication_id

    async def hello_func(ctx):
        await ctx.send(content="Mensagem com botão:")

    async def main():
        async with ClientApp(TOKEN, aplication_id) as bot:
            hello_command = Command("hello", hello_func, "Respond with 'Hello, world!'")
            bot.add_command(hello_command)
            
            await bot.sync_with_guild(GUILD_ID)  # Sincroniza comandos de barra com o servidor

            await bot.connect()

    if __name__ == "__main__":
        asyncio.run(main())


You can find more examples in the examples directory.

Links
------

- `No links!`_