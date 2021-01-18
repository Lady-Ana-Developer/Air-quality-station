import bme680
import time

print("""Estimate indoor air quality

Press Ctrl+C to exit

""")

sensor = bme680.BME680()

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

print("Calibration data:")
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print("{}: {}".format(name, value))
            
print("\n\nInitial reading:")
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print("{}: {}".format(name, value))

start_time = time.time()
curr_time = time.time()
burn_in_time = 100

burn_in_data = []

try:

    print("Collecting gas resistance burn-in data during 100 seconds")
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print("Gas: {0} Ohms".format(gas))
            time.sleep(10)

    gas_baseline = sum(burn_in_data[-50:]) / 50.0

    hum_baseline = 40.0

    hum_weighting = 0.25

    print("Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n".format(gas_baseline, hum_baseline))

    while True:
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            gas_offset = gas_baseline - gas
            
            hum = sensor.data.humidity
            hum_offset = hum - hum_baseline

            if hum_offset > 0:
                hum_score = (100 - hum_baseline - hum_offset) / (100 - hum_baseline) * (hum_weighting * 100)

            else:
                hum_score = (hum_baseline + hum_offset) / hum_baseline * (hum_weighting * 100)


            if gas_offset > 0:
                gas_score = (gas / gas_baseline) * (100 - (hum_weighting * 100))

            else:
                gas_score = 100 - (hum_weighting * 100)

            air_quality_score = hum_score + gas_score
            
            # It will print the data every fifteen minutes
            print("The temperature is {0:.2f} Celsius, The pressure is {1:.2f} hPa, The humidity is {2:.2f} %RH".format(sensor.data.temperature, sensor.data.pressure, sensor.data.humidity))
            print("Gas: {0:.2f} Ohms, Air quality: {2:.2f}".format(gas, hum, air_quality_score))
            print(".........................-------------------------------------.........................")
            
            time.sleep(900)

except KeyboardInterrupt:
    pass
