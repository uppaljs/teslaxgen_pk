"""Platform for TeslaPV inverter integration."""

from __future__ import annotations
from datetime import timedelta

import inflection
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
import homeassistant.helpers.config_validation as cv


from .const import SERVER_HOST, SERVER_PORT, LOGGER, DOMAIN, MANUFACTURER, SCAN_INTERVAL
from .server import TeslaPVServer
from .sensor_types import INVERTER_SENSOR_TYPES

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST, default=SERVER_HOST): cv.string,
        vol.Optional(CONF_PORT, default=SERVER_PORT): cv.port,
        vol.Optional(CONF_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.positive_int,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensors for the inverter platform."""

    inverter_name = config[CONF_NAME]

    if CONF_ID in config:
        inverter_id = config[CONF_ID]
    else:
        inverter_id = inflection.underscore(inverter_name)

    interval = config[CONF_SCAN_INTERVAL]

    inverter_info = DeviceInfo(
        identifiers={(DOMAIN, inverter_id)},
        manufacturer=MANUFACTURER,
        name=inverter_name,
    )

    server = TeslaPVServer(
        inverter_name,
        config[CONF_CLIENT_ID],
        config[CONF_HOST],
        config[CONF_PORT],
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
        interval,
    )

    update_coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=inverter_name,
        update_method=server.request,
        update_interval=timedelta(seconds=interval / 2),
    )

    entities = [
        TeslaPVSensor(
            update_coordinator,
            inverter_info,
            description=description,
        )
        for description in INVERTER_SENSOR_TYPES
    ]

    entity_dict = {}
    for entity in entities:
        entity_dict[entity.entity_description.mqtt_message_key] = entity

    async_add_entities(entities)

    @callback
    def on_telemetry_receive(telemetry):
        for key, value in telemetry.items():
            if key in entity_dict:
                entity = entity_dict[key]
                entity.update_value(value)

    server.on_receive = on_telemetry_receive


class TeslaPVSensor(CoordinatorEntity, SensorEntity):
    """Entity representing individual inverter sensor."""

    def __init__(
        self, update_coordinator, interver_info, description: SensorEntityDescription
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(update_coordinator)
        inverter_name = interver_info["name"]
        inverter_id = next(iter(interver_info["identifiers"]))[1]

        self.entity_description = description
        self._attr_name = f"{inverter_name} {description.name}"
        self._attr_unique_id = f"{inverter_id}_{description.key}"
        self._attr_device_info = interver_info
        self._value = None

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return self._attr_unique_id

    @property
    def native_value(self):
        """Return the value of the sensor."""
        if self._value is None:
            value = None
        else:
            value = self.entity_description.value(self._value)

        return value

    def update_value(self, value):
        """Updates the value of the sensor if its changed."""

        if value != self._value:
            self._value = value
            self.async_write_ha_state()
            LOGGER.debug(
                "Updating sensor %s with value %s", self._attr_unique_id, value
            )
