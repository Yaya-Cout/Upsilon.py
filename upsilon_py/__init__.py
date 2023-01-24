#!/usr/bin/env python3
"""Python script to use Upsilon.js from Python."""
# Standard library imports
import asyncio
import json
import logging
import os

import rich.logging

logger = logging.getLogger(__name__)


class JavaScriptError(Exception):
    """JavaScript error."""

    def __init__(self, message):
        """Initialize the JavaScriptError object."""
        super().__init__(message)


class NumWorks:
    """NumWorks object."""

    def __init__(self) -> None:
        """Initialize the NumWorks object."""
        logger.info("Initializing NumWorks object")
        # Process
        self.proc = None

        # Writer and reader
        self.writer = None
        self.reader = None
        self.stderr = None

        self.ready = asyncio.Event()

        # Asyncio queue
        self._queue = asyncio.Queue()

    async def start(self) -> None:
        """Start the NumWorks object."""
        logger.info("Starting NumWorks object")
        # Get npm global install path (command : npm root --quiet -g)
        npm_global_path = os.popen("npm root --quiet -g").read().strip()

        # Create the javascript daemon
        self.proc = await asyncio.create_subprocess_exec(
            "node", os.path.join(os.path.dirname(__file__), "main.js"),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=512 * 1024,
            env={
                "NODE_PATH": npm_global_path
            }
        )

        # Redirect the stdin and stdout
        self.writer = self.proc.stdin
        self.reader = self.proc.stdout
        self.stderr = self.proc.stderr

        # Redirect the stderr to the logger (to avoid invisible errors)
        asyncio.ensure_future(self._redirect_stderr())

        # Ensure the read task
        asyncio.ensure_future(self._read())

        # Wait to receive the "{ "ready": true }" message
        asyncio.ensure_future(self._wait_for_ready())

    async def stop(self) -> None:
        """Stop the NumWorks object."""
        logger.info("Stopping NumWorks object")

        # Disconnect from the NumWorks
        await self.disconnect()

        # Send the EOF
        self.writer.write_eof()

        # Close the writer
        self.writer.close()

        # Wait for the process to terminate
        # await self.proc.wait()

        self.ready.clear()

    async def _wait_for_ready(self) -> None:
        """Wait for the ready message."""
        while True:
            # Get the data
            data = await self._queue.get()

            # Check the data
            if data.get("ready", False):
                self.ready.set()
                break

    async def _redirect_stderr(self) -> None:
        """Redirect the stderr to the logger."""
        while True:
            # Read the data
            data = await self.stderr.readline()

            # Decode the data
            data = data.decode("utf-8").strip()

            # Ignore empty data
            if data == "":
                continue

            # Log the data
            logger.error(data)

    async def _read(self) -> None:
        """Read the data from the NumWorks."""
        while True:
            # Read the data
            data = await self.reader.readline()

            # Decode the data
            data = data.decode("utf-8").strip()

            # Try to load the data
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON data: %s", data)
                continue

            # Put the data in the queue
            await self._queue.put(data)

    async def _write(self, data: dict) -> None:
        """Write the data to the NumWorks."""
        # Dump the data
        data = json.dumps(data)

        # Write the data
        self.writer.write(data.encode("utf-8"))

        # Write the newline
        self.writer.write(b"\n")

        # Flush the writer
        await self.writer.drain()

    async def _get_result(self) -> dict:
        """Get the result from the queue."""
        # Get the result
        result = await self._queue.get()

        if isinstance(result, dict) and result.get("error", False):
            raise JavaScriptError(result["error"])

        # Return the result
        return result

    async def connect(self) -> dict[str, str]:
        """Connect to the NumWorks."""
        logger.info("Connecting to the NumWorks")
        await self.ensure_ready()
        # Create the command
        command = {
            "method": "connect"
        }

        # Send the command
        await self._write(command)

        # Return the result
        return await self._get_result()

    async def disconnect(self) -> dict[str, str]:
        """Disconnect from the NumWorks."""
        logger.info("Disconnecting from the NumWorks")
        await self.ensure_ready()
        # Create the command
        command = {
            "method": "disconnect"
        }

        # Send the command
        await self._write(command)

        # Return the result
        return await self._get_result()

    async def status(self) -> dict[str, str]:
        """Get the status of the NumWorks."""
        logger.info("Getting the status of the NumWorks")
        await self.ensure_ready()
        # Create the command
        command = {
            "method": "status"
        }

        # Send the command
        await self._write(command)

        # Return the result
        return await self._get_result()

    async def get_model(self) -> int:
        """Get the model of the NumWorks."""
        logger.info("Getting the model of the NumWorks")
        await self.ensure_connected()
        # Create the command
        command = {
            "method": "getModel"
        }

        # Send the command
        await self._write(command)

        # Return the result
        return await self._get_result()

    async def get_platform_info(self) -> dict:
        """Get the platformInfo of the NumWorks."""
        await self.ensure_connected()
        logger.info("Getting the platformInfo of the NumWorks")
        # Create the command
        command = {
            "method": "getPlatformInfo"
        }

        # Send the command
        await self._write(command)

        # Return the result
        return await self._get_result()

    async def backup_storage(self) -> dict:
        """Backup the storage of the NumWorks."""
        logger.info("Backing up the storage of the NumWorks")
        await self.ensure_connected()
        # Create the command
        command = {
            "method": "backupStorage"
        }

        # Send the command
        await self._write(command)

        # Return the result
        return await self._get_result()

    async def install_storage(self, storage: dict) -> dict[str, str]:
        """Install the storage on the NumWorks."""
        logger.info("Installing the storage on the NumWorks")
        await self.ensure_connected()
        # Create the command
        command = {
            "method": "installStorage",
            "args": [storage]
        }

        # Send the command
        await self._write(command)

        # Return the result
        return await self._get_result()

    async def ensure_ready(self) -> None:
        """Ensure the subprocess is ready."""
        await self.ready.wait()

    async def ensure_connected(self) -> None:
        """Ensure the NumWorks is connected."""
        await self.ensure_ready()

        # Get the status
        logger.disabled = True
        status = await self.status()
        logger.disabled = False

        # Check the status
        if not status["status"]:
            await self.connect()

    # TODO: Add flashInternal and flashExternal
