import asyncio
from discord.bot import ClientApp, Command, Embed, SelectMenuBuilder

TOKEN = 'MTAyNTgwMTAyOTU2NjA3MDgyNA.GiVUVh.2Flq4ppoN8HTO6g8LKvQEUPhAEnvQKR8oCgRb0'
GUILD_ID = "898335285719470080"
aplication_id = 1025801029566070824

components = [
    {
        "type": 1,  # Action Row
        "components": [
            {
                "type": 2,  # Botão
                "label": "Clique aqui",
                "style": 1,  # Estilo primário (verde)
                "custom_id": "meu_botao"
            }
        ]
    }
]

async def handle_button_click(ctx, interaction_data):
	# Implemente a lógica para lidar com interações de botões aqui
	await ctx.send(content="Mensagem com botão:")

async def handle_on_select_menu(ctx, interaction_data):
	await ctx.send(content="Menu select")

async def hello_func(ctx):
	embed = Embed(title="Olá, mundo!", description="Esta é uma mensagem com um embed.", color=0x00FF00)
	options = [
		{"label": "Opção 1", "value": "option1"},
		{"label": "Opção 2", "value": "option2"},
		{"label": "Opção 3", "value": "option3"},
	]

	select_menu = SelectMenuBuilder.create_select_menu("my_select_menu", options, "Escolha uma opção")
	await ctx.send(content="Mensagem com botão:", embed=embed, components=[select_menu], ephemeral=False)

async def main():
	async with ClientApp(TOKEN, aplication_id) as bot:
		hello_command = Command("hello", hello_func, "Respond with 'Hello, world!'")
		bot.add_command(hello_command)
		bot.on_button_click = handle_button_click  # Associe o evento ao manipulador
		bot.on_select_menu = handle_on_select_menu
		
		await bot.sync_with_guild(GUILD_ID)  # Sincroniza comandos de barra com o servidor

		await bot.connect()

if __name__ == "__main__":
	asyncio.run(main())