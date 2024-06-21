"""Define constants for the TeslaPV (Pakistan) inverter component."""

from logging import Logger, getLogger
from homeassistant.const import Platform

DEFAULT_NAME = "TeslaPV PK"

MANUFACTURER = "Tesla PV Pakistan"

DOMAIN = "teslaxgen_pk"

SERVER_HOST = "teslasm.art"
SERVER_PORT = 1883

PLATFORMS = [Platform.SENSOR]

LOGGER: Logger = getLogger(__package__)

SCAN_INTERVAL = 300
