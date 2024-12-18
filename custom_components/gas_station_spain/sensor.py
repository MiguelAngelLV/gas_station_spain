import logging
from datetime import timedelta
from typing import Mapping, Any

from .const import (
    CONF_MUNICIPALITY,
    CONF_STATION,
    CONF_PRODUCT,
    UPDATE_INTERVAL, CONF_FIXED_DISCOUNT, CONF_PERCENTAGE_DISCOUNT, CONF_SHOW_IN_MAP
)

from .lib.gas_stations_api import GasStationApi

from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from homeassistant.const import (
    CURRENCY_EURO,
)

from homeassistant.components.sensor import (
    SensorEntityDescription, SensorEntity, SensorStateClass
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    show_in_map = entry.data[CONF_SHOW_IN_MAP]
    station = entry.data[CONF_STATION]
    product = entry.data[CONF_PRODUCT]
    municipality = entry.data[CONF_MUNICIPALITY]
    fixed_discount = entry.data[CONF_FIXED_DISCOUNT]
    percentage_discount = entry.data[CONF_PERCENTAGE_DISCOUNT]

    _LOGGER.info(f"Creating Gas Station Spain sensor with station={station} and product={product}")

    coordinator = GasStationCoordinator(hass, municipality, station, product)
    await coordinator.async_config_entry_first_refresh()

    sensor = GasStationSensor(entry.title, entry.unique_id, fixed_discount, percentage_discount, show_in_map, coordinator)
    async_add_entities([sensor])


class GasStationCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, municipality, station, product):
        super().__init__(hass=hass, logger=_LOGGER, name="Gas Station", update_interval=timedelta(hours=UPDATE_INTERVAL))
        self._latitude = None
        self._longitude = None
        self.original_price = None
        self._station = station
        self._product = product
        self._municipality = municipality

    async def async_config_entry_first_refresh(self) -> None:
        gas_station = await GasStationApi.get_gas_station(self._municipality, self._product, self._station)
        self._latitude = gas_station.latitude
        self._longitude = gas_station.longitude
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self):
        price = await GasStationApi.get_gas_price(self._station, self._municipality, self._product)
        _LOGGER.debug(f"Updated station={self._station} and product={self._product} with original price={price}")
        return {
            'price': price,
            'latitude': self._latitude,
            'longitude': self._longitude
        }


class GasStationSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, name: str, unique_id: str, fixed_discount, percentage_discount, show_in_map, coordinator):
        super().__init__(coordinator=coordinator)
        self._state = None
        self._original_price = None
        self._fixed_discount = fixed_discount
        self._percentage_discount = percentage_discount
        self._attrs: dict[str, Any] = {}
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._show_in_map = show_in_map
        self.entity_description = SensorEntityDescription(
            key=name,
            icon="mdi:gas-station",
            native_unit_of_measurement=CURRENCY_EURO,
            state_class=SensorStateClass.MEASUREMENT
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        self._state = (data['price'] - self._fixed_discount) * (1.0 - self._percentage_discount / 100.0)
        self._attrs['Precio Original'] = data['price']

        if self._show_in_map:
            self._attrs['latitude'] = data['latitude']
            self._attrs['longitude'] = data['longitude']

        self.async_write_ha_state()

    @property
    def native_value(self) -> StateType:
        return self._state

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self._attrs
