import logging
from datetime import timedelta
from typing import Mapping, Any

from .const import (
    CONF_MUNICIPALITY,
    CONF_STATION,
    CONF_PRODUCT,
    UPDATE_INTERVAL
)

from .lib.gas_stations_api import GasStationApi

from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from homeassistant.const import (
    CURRENCY_EURO,
)

from homeassistant.components.sensor import (
    SensorEntityDescription, SensorEntity, STATE_CLASS_MEASUREMENT
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    municipality = entry.data[CONF_MUNICIPALITY]
    station = entry.data[CONF_STATION]
    product = entry.data[CONF_PRODUCT]

    _LOGGER.info(f"Creating Gas Station Spain sensor with station={station} and product={product}")

    coordinator = GasStationCoordinator(hass, municipality, station, product)
    await coordinator.async_config_entry_first_refresh()

    sensor = GasStationSensor(entry.title, entry.unique_id, coordinator)
    async_add_entities([sensor])


class GasStationCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, municipality, station, product):
        super().__init__(hass=hass, logger=_LOGGER, name="Gas Station", update_interval=timedelta(hours=UPDATE_INTERVAL))
        self._municipality = municipality
        self._station = station
        self._product = product
        self._price = None

    async def _async_update_data(self):
        self._price = await GasStationApi.get_gas_price(self._station, self._municipality, self._product)
        _LOGGER.debug(f"Updated station={self._station} and product={self._product} with price={self._price}")
        return self._price


class GasStationSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, name: str, unique_id: str, coordinator):
        super().__init__(coordinator=coordinator)
        self._state = None
        self._attrs: Mapping[str, Any] = {}
        self._attr_name = name
        self._attr_unique_id = unique_id
        self.entity_description = SensorEntityDescription(
            key=name,
            icon="mdi:gas-station",
            native_unit_of_measurement=CURRENCY_EURO,
            state_class=STATE_CLASS_MEASUREMENT
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = self.coordinator.data
        self.async_write_ha_state()

    @property
    def native_value(self) -> StateType:
        return self._state
