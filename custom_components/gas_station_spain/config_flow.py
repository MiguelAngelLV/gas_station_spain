from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import callback

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
    SelectSelectorMode
)

from .const import *
from .lib.gas_stations_api import GasStationApi

_LOGGER = logging.getLogger(__name__)


class PlaceholderHub:
    def __init__(self, province: str) -> None:
        """Initialize."""
        self.province = province


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    province_id: str
    product_id: str
    municipality_id: str
    station_id: str

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            self.product_id = user_input[CONF_PRODUCT]
            self.province_id = user_input[CONF_PROVINCE]
            return await self.async_step_municipality()

        provinces = await GasStationApi.get_provinces()
        options_provinces = list(map(lambda p: SelectOptionDict(label=p.name, value=p.id), provinces))

        products = await GasStationApi.get_products()
        options_products = list(map(lambda p: SelectOptionDict(label=p.name, value=p.id), products))

        schema = vol.Schema({
            vol.Required(CONF_PRODUCT): SelectSelector(
                SelectSelectorConfig(options=options_products, multiple=False, mode=SelectSelectorMode.DROPDOWN)
            ),
            vol.Required(CONF_PROVINCE): SelectSelector(
                SelectSelectorConfig(options=options_provinces, multiple=False, mode=SelectSelectorMode.DROPDOWN)
            )
        })

        return self.async_show_form(step_id="user", data_schema=schema, last_step=False)

    async def async_step_municipality(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self.municipality_id = user_input[CONF_MUNICIPALITY]
            return await self.async_step_station()

        municipalities = await GasStationApi.get_municipalities(self.province_id)
        options = list(map(lambda p: SelectOptionDict(label=p.name, value=p.id), municipalities))
        schema = vol.Schema({
            vol.Required(CONF_MUNICIPALITY): SelectSelector(
                SelectSelectorConfig(options=options, multiple=False, mode=SelectSelectorMode.DROPDOWN)
            )
        })
        return self.async_show_form(step_id="municipality", data_schema=schema)

    async def async_step_station(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self.station_id = user_input[CONF_STATION]
            name = await GasStationApi.get_station_name(station_id=self.station_id, municipality_id=self.municipality_id, product_id=self.product_id)

            await self.async_set_unique_id(name.id)

            return self.async_create_entry(title=name.name, data={
                CONF_PRODUCT: self.product_id,
                CONF_MUNICIPALITY: self.municipality_id,
                CONF_STATION: user_input[CONF_STATION]
            })

        stations = await GasStationApi.get_gas_stations(municipality_id=self.municipality_id, product_id=self.product_id)
        options = list(map(lambda p: SelectOptionDict(label=p.name + " - "+p.address, value=p.id), stations))
        schema = vol.Schema({
            vol.Required(CONF_STATION): SelectSelector(
                SelectSelectorConfig(options=options, multiple=False, mode=SelectSelectorMode.DROPDOWN)
            )
        })
        return self.async_show_form(step_id="station", data_schema=schema)

