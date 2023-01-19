#!/usr/bin/env python3
"""Python script to use Upsilon.js from Python."""
# Standard library imports
import asyncio
import logging

import rich.logging

from upsilon_py import NumWorks

logger = logging.getLogger(__name__)

# Configure the logging
logging.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[rich.logging.RichHandler(rich_tracebacks=True)]
)


async def main():
    """Main function."""
    # Create the NumWorks object
    numworks = NumWorks()

    # Start the NumWorks object
    await numworks.start()

    # Connect to the NumWorks
    logger.info(await numworks.connect())

    # Get the status
    logger.info(await numworks.status())

    # Get the model
    logger.info("Model: %s", await numworks.get_model())

    # Get the platformInfo
    logger.info("PlatformInfo: %s", await numworks.get_platform_info())

    # Backup the storage
    storage = await numworks.backup_storage()
    # logger.info("Storage: %s", storage)

    # Modify the storage
    for _ in range(1):
        storage["records"].append({
            "name": "Test",
            "type": "py",
            "autoImport": True,
            "code": "print(\"Hello World!\")"
        })

    # Install the storage
    logger.info(await numworks.install_storage(storage))

    # Disconnect from the NumWorks
    logger.info(await numworks.disconnect())

    # Wait for the NumWorks object to stop
    await numworks.stop()


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
