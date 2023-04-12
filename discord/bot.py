import asyncio, aiohttp, json
from discord.http_client import HTTPClient

class SelectMenuBuilder:
	@staticmethod
	def create_select_menu(custom_id, options, placeholder=None):
		select_menu = {
			"type": 1,
			"components": [
				{
					"type": 3,
					"custom_id": custom_id,
					"options": options,
					"placeholder": placeholder or "Selecione uma opção",
				}
			],
		}
		return select_menu

class Embed:
	def __init__(
		self,
		title=None,
		description=None,
		color=None,
		url=None,
		timestamp=None,
		fields=None,
		author=None,
		footer=None,
		thumbnail=None,
		image=None,
	):
		self.title = title
		self.description = description
		self.color = color
		self.url = url
		self.timestamp = timestamp
		self.fields = fields or []
		self.author = author
		self.footer = footer
		self.thumbnail = thumbnail
		self.image = image

	def add_field(self, name, value, inline=False):
		self.fields.append({"name": name, "value": value, "inline": inline})

	def set_author(self, name, url=None, icon_url=None):
		self.author = {"name": name, "url": url, "icon_url": icon_url}

	def set_footer(self, text, icon_url=None):
		self.footer = {"text": text, "icon_url": icon_url}

	def set_thumbnail(self, url):
		self.thumbnail = {"url": url}

	def set_image(self, url):
		self.image = {"url": url}

	def to_dict(self):
		embed_dict = {}
		if self.title:
			embed_dict["title"] = self.title
		if self.description:
			embed_dict["description"] = self.description
		if self.color:
			embed_dict["color"] = self.color
		if self.url:
			embed_dict["url"] = self.url
		if self.timestamp:
			embed_dict["timestamp"] = self.timestamp.isoformat()
		if self.fields:
			embed_dict["fields"] = self.fields
		if self.author:
			embed_dict["author"] = self.author
		if self.footer:
			embed_dict["footer"] = self.footer
		if self.thumbnail:
			embed_dict["thumbnail"] = self.thumbnail
		if self.image:
			embed_dict["image"] = self.image
		return embed_dict

class Command:
	def __init__(self, name, func, description, options=None):
		self.name = name
		self.func = func
		self.description = description
		self.options = options

class Context:
	def __init__(self, bot, message_data):
		self.bot = bot
		self.message_data = message_data
		self.channel_id = message_data["channel_id"]
		self.user_id = message_data["member"]["user"]["id"]
		self.id = message_data["id"]

	async def send(self, content=None, **kwargs):
		content=kwargs.get("content") if content is None else content
		embed=kwargs.get("embed")
		components=kwargs.get("components")
		ephemeral=kwargs.get("ephemeral")
		file=kwargs.get("file")
		tts=kwargs.get("tts")

		url = f"https://discord.com/api/v10/channels/{self.channel_id}/messages"
		headers = {"Authorization": f"Bot {self.bot.token}"}

		if embed:
			embed = embed.to_dict()

		json_payload = {
			"content": content,
			"embed": embed,
			"components": components,
			"flags": 64 if ephemeral else 0,
			"tts": tts,
		}

		if file:
			# Se um arquivo for fornecido, use multipart para enviar o arquivo junto com o payload JSON
			form_data = aiohttp.FormData()
			form_data.add_field("payload_json", json.dumps(json_payload), content_type="application/json")
			form_data.add_field("file", file, filename=file.name, content_type="application/octet-stream")

			async with aiohttp.ClientSession() as session:
				async with session.post(url, headers=headers, data=form_data) as response:
					await response.json()
		else:
			async with aiohttp.ClientSession() as session:
				async with session.post(url, headers=headers, json=json_payload) as response:
					await response.json()


class ClientApp:
	def __init__(self, token, client_id):
		self.token = token
		self.session = aiohttp.ClientSession()
		self.client_id = client_id
		self.commands = {}
		self.http = HTTPClient(token, self.session)  # Adicione essa linha
		self.on_button_click = None  # Adicione este atributo
		self.on_select_menu = None

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.session.close()

	# Dentro da classe MyBot em mybot.py
	def command(self, name=None, description=None):
		def decorator(func):
			cmd_name = name or func.__name__
			self.commands[cmd_name] = func

			if description:
				self.command_descriptions[cmd_name] = description

			return func

		return decorator

	# Dentro da classe MyBot em mybot.py
	async def on_command(self, interaction):
		command_name = interaction["data"]["name"]
		command_function = self.commands.get(command_name)

		if command_function:
			await command_function(self, interaction)
		else:
			response_data = {
				"type": 4,
				"data": {
					"content": f"Comando desconhecido: {command_name}",
				}
			}
			await self.http.send_interaction_response(interaction["id"], interaction["token"], response_data)

	async def connect(self):
		url = 'wss://gateway.discord.gg/?v=10&encoding=json'
		async with self.session.ws_connect(url) as ws:
			while True:
				data = await ws.receive_json()
				if data['op'] == 10:
					heartbeat_interval = data['d']['heartbeat_interval'] / 1000
					asyncio.create_task(self.heartbeat(ws, heartbeat_interval))
					await self.identify(ws)
				elif data['op'] == 0:
					await self.handle_event(data)
				elif data['op'] == 11:
					print("Heartbeat ACK")

	async def heartbeat(self, ws, interval):
		while True:
			await asyncio.sleep(interval)
			await ws.send_json({"op": 1, "d": None})

	async def identify(self, ws):
		payload = {
			"op": 2,
			"d": {
				"token": self.token,
				"intents": 513,  # Mude os intents conforme necessário
				"properties": {
					"$os": "linux",
					"$browser": "my_library",
					"$device": "my_library"
				}
			}
		}
		await ws.send_json(payload)
		data = await ws.receive_json()
		if data['t'] == 'READY':
			self.client_id = data['d']['user']['id']

	async def handle_event(self, data):
		if data['t'] == 'READY':
			self.client_id = data['d']['user']['id']
			print('Conectado com sucesso.')
		elif data['t'] == 'MESSAGE_CREATE':
			await self.handle_message(data['d'])
		elif data['t'] == 'INTERACTION_CREATE':
			await self.handle_interaction(data['d'])

	async def handle_message(self, message_data):
		content = message_data['content']

		if content.startswith('!'):  # Altere o prefixo do comando conforme necessário
			command_name = content[1:].split()[0]
			await self.execute_command(command_name, message_data)

	async def execute_command(self, command_name, message_data):
		command = self.commands.get(command_name)
		if command:
			ctx = self.create_context(message_data)
			await command.func(ctx)

	async def handle_interaction(self, interaction_data):
		if interaction_data['type'] == 2:  # 2 representa comandos de barra
			command_name = interaction_data['data']['name']
			await self.execute_slash_command(command_name, interaction_data)
		elif interaction_data['type'] == 3:  # 3 representa interações de componente
			if self.on_button_click and interaction_data['data']['component_type'] == 2:  # Verifique se o manipulador está definido
				ctx = self.create_context(interaction_data)
				await self.on_button_click(ctx, interaction_data)
			if self.on_select_menu  and interaction_data['data']['component_type'] == 3:  # Verifique se o manipulador está definido
				ctx = self.create_context(interaction_data)
				await self.on_select_menu(ctx, interaction_data)

	async def execute_slash_command(self, command_name, interaction_data):
		command = self.commands.get(command_name)
		if command:
			ctx = self.create_context(interaction_data)
		response = await command.func(ctx)
		await self.send_interaction_response(interaction_data['id'], interaction_data['token'], response)
	
	async def send_interaction_response(
			self,
			interaction_id,
			interaction_token,
			content=None,
			ephemeral=False,
			embed=None,
			components=None,
			):
		url = f"https://discord.com/api/interactions/{interaction_id}/{interaction_token}/callback"
		response_data = {
			"type": 4,
			"data": {
				"content": content or "",
				"flags": 64 if ephemeral else 0,
			},
		}

		if embed:
			response_data["data"]["embeds"] = [embed.to_dict()]

		if components:
			response_data["data"]["components"] = components

		await self.http.send_interaction_response(interaction_id, interaction_token, response_data)
		
		async with self.session.post(url, json=response_data) as resp:
			if resp.status != 200 and resp.status != 204:
				print(f"Erro ao enviar resposta do comando de barra: {resp.status} {await resp.text()}")

	async def create_slash_command(self, guild_id, command_name, description, options=None):
		url = f"https://discord.com/api/applications/{self.client_id}/guilds/{str(guild_id)}/commands"
		command_data = {
			"name": command_name,
			"description": description,
			"options": options or []
		}
		async with self.session.post(url, headers={"Authorization": f"Bot {self.token}"}, json=command_data) as resp:
			if resp.status != 200 and resp.status != 201:
				print(f"Erro ao criar comando de barra: {resp.status} {await resp.text()}")

	def add_command(self, command):
		self.commands[command.name] = command

	def create_context(self, message_data):
		return Context(self, message_data)

	async def send_message(self, channel_id, content=None, embed=None, components=None, ephemeral=None):
		data = {}

		if ephemeral:
			data['ephemeral'] = ephemeral
		if content:
			data['content'] = content
		if embed:
			data['embeds'] = [embed]
		if components:
			data['components'] = components

		if not data:
			print('Nenhuma informação fornecida para enviar a mensagem.')
			return
	
		async with self.session.post(f'https://discord.com/api/channels/{channel_id}/messages', headers={'Authorization': f'Bot {self.token}'}, json=data) as resp:
			if resp.status != 200 and resp.status != 201:
				print(f'Falha ao enviar mensagem: {resp.status} {await resp.text()}')

	async def sync_with_guild(self, guild_id):
		existing_commands = await self.get_guild_commands(str(guild_id))
		existing_commands_dict = {cmd['name']: cmd for cmd in existing_commands}

		for command_name, command in self.commands.items():
			if command_name in existing_commands_dict:
				existing_command = existing_commands_dict[command_name]
				await self.update_guild_command(str(guild_id), existing_command['id'], command)
			else:
				await self.create_guild_command(str(guild_id), command)

		for existing_command in existing_commands:
			if existing_command['name'] not in self.commands:
				await self.delete_guild_command(str(guild_id), existing_command['id'])

	async def get_guild_commands(self, guild_id):
		url = f"https://discord.com/api/applications/{self.client_id}/guilds/{str(guild_id)}/commands"
		async with self.session.get(url, headers={"Authorization": f"Bot {self.token}"}) as resp:
			if resp.status == 200:
				return await resp.json()
			else:
				print(f"Erro ao obter comandos da guilda: {resp.status} {await resp.text()}")
				return []

	async def create_guild_command(self, guild_id, command):
		url = f"https://discord.com/api/applications/{self.client_id}/guilds/{str(guild_id)}/commands"
		command_data = {
			"name": command.name,
			"description": command.description,
			"options": command.options or []
		}
		async with self.session.post(url, headers={"Authorization": f"Bot {self.token}"}, json=command_data) as resp:
			if resp.status != 200 and resp.status != 201:
				print(f"Erro ao criar comando de barra: {resp.status} {await resp.text()}")

	async def update_guild_command(self, guild_id, command_id, command):
		url = f"https://discord.com/api/applications/{self.client_id}/guilds/{str(guild_id)}/commands/{command_id}"
		command_data = {
			"name": command.name,
			"description": command.description,
			"options": command.options or []
		}
		async with self.session.patch(url, headers={"Authorization": f"Bot {self.token}"}, json=command_data) as resp:
			if resp.status != 200:
				print(f"Erro ao atualizar comando de barra: {resp.status} {await resp.text()}")

	async def delete_guild_command(self, guild_id, command_id):
		url = f"https://discord.com/api/applications/{self.client_id}/guilds/{str(guild_id)}/commands/{command_id}"
		async with self.session.delete(url, headers={"Authorization": f"Bot {self.token}"}) as resp:
			if resp.status != 200:
				print(f"Erro ao excluir comando de barra: {resp.status} {await resp.text()}")
