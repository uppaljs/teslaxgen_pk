"""TeslaPV inverter sensor types."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any


from homeassistant.backports.enum import StrEnum
from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription
from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    FREQUENCY_HERTZ,
    PERCENTAGE,
    POWER_WATT,
)


class GridMode(StrEnum):
    """Describes enum for grid."""

    DISCONNECTED = "disconnected"
    CONSUMING = "consuming"
    FEEDING = "feeding"
    UNKNOWN = "unknown"


def grid_mode(int_mode):
    """Converts numeric mode to descriptive enum."""
    mode_mapping = {
        0: GridMode.DISCONNECTED,
        1: GridMode.CONSUMING,
        2: GridMode.FEEDING,
    }

    return mode_mapping.get(int_mode, GridMode.UNKNOWN)


class BatteryMode(StrEnum):
    """Describes enum for grid."""

    DISCONNECTED = "disconnected"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    UNKNOWN = "unknown"


def battery_mode(int_mode):
    """Converts numeric mode to descriptive enum."""
    mode_mapping = {
        0: BatteryMode.DISCONNECTED,
        1: BatteryMode.CHARGING,
        2: BatteryMode.DISCHARGING,
    }

    return mode_mapping.get(int_mode, BatteryMode.UNKNOWN)


@dataclass
class TeslaKeysMixin:
    """Mixin for required keys."""

    mqtt_message_key: str


@dataclass
class TeslaPVSensorEntityDescription(SensorEntityDescription, TeslaKeysMixin):
    """Describes TeslaPV sensor entity."""

    value: Callable[[Any], Any] = lambda val: val


INVERTER_SENSOR_TYPES: tuple[TeslaPVSensorEntityDescription, ...] = (
    TeslaPVSensorEntityDescription(
        key="grid_voltage",
        name="Grid voltage",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        mqtt_message_key="grid.v",
    ),
    TeslaPVSensorEntityDescription(
        key="grid_watts",
        name="Grid consumption/production",
        native_unit_of_measurement=POWER_WATT,
        device_class=SensorDeviceClass.POWER,
        mqtt_message_key="grid.w",
    ),
    TeslaPVSensorEntityDescription(
        key="grid_frequency",
        name="Grid frequency",
        native_unit_of_measurement=FREQUENCY_HERTZ,
        icon="mdi:current-ac",
        mqtt_message_key="grid.f",
    ),
    TeslaPVSensorEntityDescription(
        key="grid_percentage",
        name="Grid percentage",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        mqtt_message_key="grid.pt",
    ),
    TeslaPVSensorEntityDescription(
        key="grid_mode",
        name="Grid mode",
        value=grid_mode,
        mqtt_message_key="grid.d",
    ),
    TeslaPVSensorEntityDescription(
        key="load_voltage",
        name="Load voltage",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        mqtt_message_key="load.v",
    ),
    TeslaPVSensorEntityDescription(
        key="load_watts",
        name="Load",
        native_unit_of_measurement=POWER_WATT,
        device_class=SensorDeviceClass.POWER,
        mqtt_message_key="load.w",
    ),
    TeslaPVSensorEntityDescription(
        key="load_frequency",
        name="Load frequency",
        native_unit_of_measurement=FREQUENCY_HERTZ,
        icon="mdi:information-outline",
        mqtt_message_key="load.f",
    ),
    TeslaPVSensorEntityDescription(
        key="load_percentage",
        name="Load percentage",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        mqtt_message_key="load.pt",
    ),
    TeslaPVSensorEntityDescription(
        key="battery_voltage",
        name="Battery voltage",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        value=lambda v: v / 10,
        mqtt_message_key="battery.v",
    ),
    TeslaPVSensorEntityDescription(
        key="battery_percentage",
        name="Battery percentage",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        mqtt_message_key="battery.pt",
    ),
    TeslaPVSensorEntityDescription(
        key="battery_mode",
        name="Battery mode",
        value=battery_mode,
        mqtt_message_key="battery.d",
    ),
    TeslaPVSensorEntityDescription(
        key="solar_voltage",
        name="Solar voltage",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        mqtt_message_key="pv.v",
    ),
    TeslaPVSensorEntityDescription(
        key="solar_watts",
        name="Solar production",
        native_unit_of_measurement=POWER_WATT,
        device_class=SensorDeviceClass.POWER,
        mqtt_message_key="pv.w",
    ),
    TeslaPVSensorEntityDescription(
        key="solar_energy_total",
        name="Energy total",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        mqtt_message_key="oth.et",
    ),
    TeslaPVSensorEntityDescription(
        key="solar_energy_year",
        name="Energy this year",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        mqtt_message_key="oth.ey",
    ),
    TeslaPVSensorEntityDescription(
        key="solar_energy_month",
        name="Energy this month",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        mqtt_message_key="oth.em",
    ),
    TeslaPVSensorEntityDescription(
        key="solar_energy_today",
        name="Energy today",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        mqtt_message_key="oth.ed",
    ),
)
