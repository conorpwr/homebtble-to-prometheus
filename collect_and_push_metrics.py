# Simple bluetooth LE advertisement parser for BTHomev2 devices
# Pushes data to a prometheus pushgateway
# Conor Power

import logging
import asyncio

from bleak import BleakScanner
from bthome import parse_payload

from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway

# Devices to watch for announcements from
# MAC Address: Friendly name
known_device = {
  '00:00:00:00:00:00': 'My name for this sensor',
  }

# This is the UUID the BLE advertisement is on
known_service_uuid = '0000fcd2-0000-1000-8000-00805f9b34fb'

# Address of prometheus pushgateway
pushgateway_endpoint = '192.0.2.1:9091'

def configure_logging():
  logging.basicConfig(format='%(levelname)s:%(message)s', filename='gather_ble_adv.log', level=logging.INFO)
  logging.getLogger(__name__)
  logging.info('Starting up...')

async def get_adv():
  while True:
    temp = {}
    humidity = {}

    result = await BleakScanner.discover(timeout=10, return_adv=True)
    for dev, adv in result.values():
      if dev.address in known_device:
        logging.debug(f"Matched device: {dev.address} dev: {dev} adv: {adv}")
        registry = CollectorRegistry()

        data = adv.service_data.get(known_service_uuid) 
        if data is None:
          logging.warn(f"Unknown service_uuid device: {dev.address} dev: {dev} adv: {adv}")
          continue

        try:
          # This is my terrible hackjob on https://github.com/custom-components/ble_monitor/
          # This assumes a BTHomev2 protocol and handles nothing else
          decoded = parse_payload(data[5:], 2)
        except:
          logging.exception(f"parse_payload failed for device: {dev.address} dev: {dev} adv: {adv}")

        if decoded is None:
          logging.warning(f"No parsable response for device: {dev.address} dev: {dev} adv: {adv}")
          continue

        logging.debug(f"Device: {known_device[dev.address]} Decoded: {decoded}")
        for measurement, result in decoded.items():
          if measurement == "temperature":
            temp[known_device[dev.address]] = round(result, 1)
            t = Gauge('sensor_temperature', 'Temperature', ['location'], registry=registry)
            t.labels(location=f"{known_device[dev.address]}").set(temp[known_device[dev.address]])
          elif measurement == "humidity":
            humidity[known_device[dev.address]] = round(result, 1)
            h = Gauge('sensor_humidity', 'Humidity', ['location'], registry=registry)
            h.labels(location=f"{known_device[dev.address]}").set(temp[known_device[dev.address]])
          else:
            logging.warning(f"Unknown measurement type: {measurement} for device: {dev.address} dev: {dev} adv: {adv}")

        # Prometheus pushgateway grouping logic is odd (to me at least). Without a group_key metrics will overwrite themselves even with distinct labels set
        # https://github.com/prometheus/pushgateway/issues/65 - See pushgateway readme about "grouping key"
        gkey = {'instance':known_device[dev.address]}
        try:
          pushadd_to_gateway(pushgateway_endpoint, job='ble-listener', registry=registry, grouping_key=gkey)
        except:
          logging.exception('pushadd_to_gateway failed')
          continue

        logging.debug(f"Metric pushed for: {known_device[dev.address]}")

# This needs to be a proper daemon. Some day.
if __name__=='__main__':
  configure_logging()
  asyncio.run(get_adv())
