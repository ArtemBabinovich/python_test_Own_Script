import asyncio
import json
import logging


class Lamp:
    def __init__(self, host='127.0.0.1', port=9999):
        self._host = host
        self._port = port
        self._reader = None
        self._writer = None
        self._is_on = False
        self._color = 'white'
        self._supported_commands = {
            'ON': self.turn_on,
            'OFF': self.turn_off,
            'COLOR': self.change_color,
        }

    async def connect(self):
        try:
            self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
            logging.info(f'Connected to {self._host}:{self._port}')
        except ConnectionRefusedError:
            logging.error(f'Failed to connect to {self._host}:{self._port}')

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
        await self.connect()

        while True:
            try:
                data = await self._reader.readline()
                if not data:
                    break
                await self.handle_command(data.decode().strip())
            except ConnectionResetError:
                logging.error(f'Connection to {self._host}:{self._port} reset')
                await self.connect()
            except asyncio.CancelledError:
                logging.info('Lamp connection closed')
                self._writer.close()
                await self._writer.wait_closed()
                break
            except Exception as e:
                logging.error(f'Unhandled exception: {e}')


if __name__ == '__main__':
    lamp = Lamp()
    asyncio.run(lamp.connect())
