"""Support for Switchbot API sensors."""
from datetime import date, datetime
from decimal import Decimal

from .switchbotapi import SwitchBot

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
                        switchbot, device["device_id"], device["device_name"], devices.__len__()*2
                    )
                ],
                True,
            )
            add_entities(
                [
                    SwitchbotHumiditySensor(
                        switchbot, device["device_id"], device["device_name"], devices.__len__()*2
                    )
                ],
                True,
            )


class SwitchbotSensor(SensorEntity):
    """Base class for switchbot sensors."""
    
    _attr_has_entity_name = True
    lastUpdated : datetime | None = None 
    requestTimeout : int = 10

    def __init__(self, switchbot, device_id, device_name, number_of_devices, device_prefix) -> None:
        """Initialize the sensor."""
        self.number_of_devices = number_of_devices
        self._attr_name = device_name
        self._attr_unique_id = device_prefix + device_id
        self._attr_native_value = 0
        self.switchbot = switchbot
        self.device_id = device_id

        #switchbot allows 10000 requests per day, so we need an apprioriate timeout
        requests = self.number_of_devices + 1
        updatesPerDay = 10000 / requests
        self.requestTimeout = 86400 / updatesPerDay

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the state of the sensor."""
        return self._attr_native_value
    
    def update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            if self.lastUpdated is not None and (datetime.now() - self.lastUpdated).seconds < self.requestTimeout:
                return
            response = self.switchbot.client.get("devices/" + self.device_id + "/status")
            self._attr_native_value = self.extractValueFromResponse(response)
            self.lastUpdated = datetime.now()
        except RuntimeError as err:
            if "daily limit" in str(err):
                return
            raise err
        
    def extractValueFromResponse(self, response):
        pass

class SwitchbotTemperatureSensor(SwitchbotSensor):
    """Representation of a Switchbot API temperature sensor."""

    def __init__(self, switchbot, device_id, device_name, number_of_devices) -> None:
        """Initialize the sensor."""
        super().__init__(switchbot, device_id, device_name, number_of_devices, "switchbot_temperature_")

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "°C"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        return SensorDeviceClass.TEMPERATURE
    
    def extractValueFromResponse(self, response):
        return response["body"]["temperature"]


class SwitchbotHumiditySensor(SwitchbotSensor):
    """Representation of a Switchbot API humidity sensor."""

    def __init__(self, switchbot, device_id, device_name,number_of_devices) -> None:
        """Initialize the sensor."""
        super().__init__(switchbot, device_id, device_name, number_of_devices, "switchbot_humidity_")

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        return SensorDeviceClass.HUMIDITY
        
    def extractValueFromResponse(self, response):
        return response["body"]["humidity"]    
