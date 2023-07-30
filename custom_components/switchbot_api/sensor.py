"""Support for Switchbot API sensors."""
from datetime import date, datetime
from decimal import Decimal

from switchbot import SwitchBot

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Switchbot API sensor."""
    await setup_platform(hass, entry.as_dict(), async_add_entities, None)


async def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Switchbot API sensor."""

    token = config["data"]["token"]
    secret = config["data"]["secret"]

    switchbot = SwitchBot(token, secret)

    response = await hass.async_add_executor_job(
        lambda: switchbot.client.get("devices")
    )
    devices = response["body"]["device_list"]
    for device in devices:
        if device["device_type"] in ("MeterPlus", "WoIOSensor"):
            add_entities(
                [
                    SwitchbotTemperatureSensor(
                        switchbot, device["device_id"], device["device_name"]
                    )
                ],
                True,
            )
            add_entities(
                [
                    SwitchbotHumiditySensor(
                        switchbot, device["device_id"], device["device_name"]
                    )
                ],
                True,
            )


class SwitchbotTemperatureSensor(SensorEntity):
    """Representation of a Switchbot API temperature sensor."""

    _attr_has_entity_name = True

    def __init__(self, switchbot, device_id, device_name) -> None:
        """Initialize the sensor."""
        self._attr_name = device_name
        self._attr_unique_id = "switchbot_temperature_" + device_id
        self._attr_native_value = 0
        self.switchbot = switchbot
        self.device_id = device_id

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the state of the sensor."""
        return self._attr_native_value

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "°C"

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        response = self.switchbot.client.get("devices/" + self.device_id + "/status")
        self._attr_native_value = response["body"]["temperature"]

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        return SensorDeviceClass.TEMPERATURE


class SwitchbotHumiditySensor(SensorEntity):
    """Representation of a Switchbot API humidity sensor."""

    _attr_has_entity_name = True

    def __init__(self, switchbot, device_id, device_name) -> None:
        """Initialize the sensor."""
        self._attr_name = device_name
        self._attr_unique_id = "switchbot_humidity_" + device_id
        self._attr_native_value = 0
        self.switchbot = switchbot
        self.device_id = device_id

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the state of the sensor."""
        return self._attr_native_value

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        return SensorDeviceClass.HUMIDITY

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        response = self.switchbot.client.get("devices/" + self.device_id + "/status")
        self._attr_native_value = response["body"]["humidity"]
