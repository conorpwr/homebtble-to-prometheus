from bthome import parse_payload

# Should return a dictionary of {'temperature': 28.14, 'humidity': 39.7}
def test_parser():
  binary = b'@\x00A\x01d\x02\xfe\n\x03\x82\x0f'
  decoded = parse_payload(binary[5:], 2)
  assert (decoded['temperature'] == 28.14) and (decoded['humidity'] == 39.7)
