# Componente Gas Station Spain


## ¿Qué es Gas Station Spain?

Es un componente para [Home Assistant](https://home-assistant.io/) que permite obtener el precio del combustible de las distintas
gasolineras de España para visualziarlo en tu instalación de Home Assistant.



## Instalación

Puedes instalar el componente usando HACS:

### Directa usando _My Home Assistant_
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=miguelangellv&repository=gas_station_spain&category=integration)


### Manual
Deberás añadir el repositorio personalizado en HACS:

```
HACS -> Integraciones -> Tres puntitos -> Repositorios Personalizados
```
Copias la URL del reposotiro ( https://github.com/MiguelAngelLV/gas_station_spain ), como categoría seleccionas _Integración_ y pulsas en _Añadir_.

Una vez añadido el repositorio, lo instalas.


## Configuración

Una vez instalado, ve a _Dispositivos y Servicios -> Añadir Integración_ y busca _Gasolineras España_.

El asistente te irá solicitando los datos de la gasolinera y el tipo de combustible. 

Una vez configurado, tendrás la integración con la entidad que muestre el precio.

Puedes añadir varias configuraciones para controlar varios precios (distintas gasolineras y distintos combustibles).
