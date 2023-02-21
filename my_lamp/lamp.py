import aiohttp
import asyncio
import json
import logging


class Lamp:
    def __init__(self, host='127.0.0.1', port=9999):
        self._host = host
        self._port = port
        self._is_on = False
        self._color = 'white'
        self._supported_commands = {
            'ON': self.turn_on,
            'OFF': self.turn_off,
            'COLOR': self.change_color,
        }

    async def handle_command(self, command):
        try:
            command = json.loads(command)
        except ValueError:
            logging.warning('Invalid JSON format')
            return

        if 'command' not in command:
            logging.warning('No command provided')
            return

        if command['command'] not in self._supported_commands:
            logging.warning(f'Unknown command: {command["command"]}')
            return

        await self._supported_commands[command['command']](command.get('metadata'))

    async def turn_on(self, metadata):
        self._is_on = True
        logging.info('Lamp turned on')

    async def turn_off(self, metadata):
        self._is_on = False
        logging.info('Lamp turned off')

    async def change_color(self, metadata):
        if metadata:
            self._color = metadata
            logging.info(f'Color changed to {metadata}')
        else:
            logging.warning('No color provided')

    async def run(self):
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{self._host}:{self._port}"
                async with session.ws_connect(url) as ws:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = msg.data.strip()
                            await self.handle_command(data)
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            logging.error(f'Connection to {self._host}:{self._port} closed')
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logging.error(f'Connection to {self._host}:{self._port} error')
                            break
        except aiohttp.client_exceptions.ClientConnectorError as e:
            logging.error(f'Error connecting to {self._host}:{self._port}: {e}')
            return


if __name__ == '__main__':
    lamp = Lamp()
    asyncio.run(lamp.run())
