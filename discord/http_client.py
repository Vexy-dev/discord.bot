import aiohttp
import json

API_BASE_URL = "https://discord.com/api/v10"


class HTTPClient:
	def __init__(self, token, session):
		self.token = token
		self.session = session

	async def request(self, method, path, **kwargs):
		headers = kwargs.get("headers", {})
		headers["Authorization"] = f"Bot {self.token}"
		headers["Content-Type"] = "application/json"
		kwargs["headers"] = headers

		if "json" in kwargs:
			kwargs["data"] = json.dumps(kwargs["json"])
			del kwargs["json"]

		url = API_BASE_URL + path
		async with self.session.request(method, url, **kwargs) as response:
			if response.status >= 300:
				raise Exception(f"Erro ao fazer requisição: {response.status} {await response.text()}")
			if response.status == 204:
				return None
			return await response.json()

	async def send_interaction_response(self, interaction_id, interaction_token, response_data):
		path = f"/interactions/{interaction_id}/{interaction_token}/callback"
		return await self.request("POST", path, json=response_data)

	async def create_guild_command(self, guild_id, command_data):
		path = f"/applications/{self.token}/guilds/{guild_id}/commands"
		return await self.request("POST", path, json=command_data)

	async def get_guild_commands(self, guild_id):
		path = f"/applications/{self.token}/guilds/{guild_id}/commands"
		return await self.request("GET", path)

	async def delete_guild_command(self, guild_id, command_id):
		path = f"/applications/{self.token}/guilds/{guild_id}/commands/{command_id}"
		return await self.request("DELETE", path)
