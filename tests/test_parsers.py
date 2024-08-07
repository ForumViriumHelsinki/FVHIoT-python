# Test cases for all parser modules
import pytest

from fvhiot.parsers import dlmbx
from fvhiot.parsers import paxcounter
from fvhiot.parsers import sensornode
from fvhiot.parsers import milesight

TS = "2024-02-29T12:21:30.123000+00:00"

"""
Some dlmbx examples:
02012f000304d200010bb1:1 --> [
  {
    "time": "2022-03-02T12:21:30.123000+00:00",
    "data": {
      "dl_id": 303,
      "protocol": 2,
      "distance": 1234,
      "valid_samples": 1,
      "batt": 2.993
    }
  }
]
02012f00020bb1:1 --> [
  {
    "time": "2022-03-02T12:21:30.123000+00:00",
    "data": {
      "dl_id": 303,
      "protocol": 2,
      "batt": 2.993
    }
  }
]
0218d7000309d5000f0ac4:1 --> [
  {
    "time": "2022-03-02T12:21:30.123000+00:00",
    "data": {
      "dl_id": 6359,
      "protocol": 2,
      "distance": 2517,
      "valid_samples": 15,
      "batt": 2.756
    }
  }
]
"""


class TestDlmbx:
    def test_dlmbx_01(self):
        d = dlmbx.create_datalines("02012f000304d200010bb1", 1, TS)
        assert 303 == d[0]["data"]["dl_id"]
        assert 2 == d[0]["data"]["protocol"]
        assert 1234 == d[0]["data"]["distance"]
        assert 1 == d[0]["data"]["valid_samples"]
        assert 2.993 == d[0]["data"]["batt"]
        assert TS == d[0]["time"]

    def test_dlmbx_02(self):
        d = dlmbx.create_datalines("0218d7000309d5000f0ac4", 1, TS)
        assert 6359 == d[0]["data"]["dl_id"]
        assert 2 == d[0]["data"]["protocol"]
        assert 2517 == d[0]["data"]["distance"]
        assert 15 == d[0]["data"]["valid_samples"]
        assert 2.756 == d[0]["data"]["batt"]
        assert TS == d[0]["time"]

    def test_dlmbx_no_distance(self):
        d = dlmbx.create_datalines("02012f00020bb1", 1, TS)
        assert 303 == d[0]["data"]["dl_id"]
        assert 2 == d[0]["data"]["protocol"]
        assert 2.993 == d[0]["data"]["batt"]
        assert TS == d[0]["time"]


class TestSensornode:

    def test_lat_lon(self):
        d = sensornode.create_datalines("90e12357f20e0140010205", 10, TS)
        assert 60.1985024 == d[0]["data"]["lat"]
        assert 25.0763008 == d[0]["data"]["lon"]
        assert 2 == len(d[0]["data"])
        assert TS == d[0]["time"]

    def test_lat_lon_batt_temp_in(self):
        d = sensornode.create_datalines("01e32337f80e14941228ba01295701", 10, TS)
        assert 60.2079488 == d[0]["data"]["lat"]
        assert 25.1148032 == d[0]["data"]["lon"]
        assert 4.756 == d[0]["data"]["batt"]
        assert 4.42 == d[0]["data"]["temp_in"]
        assert 3.43 == d[0]["data"]["temp_out1"]
        assert 5 == len(d[0]["data"])
        assert TS == d[0]["time"]

    def test_temprh_temp_rh_temp_out1(self):
        d = sensornode.create_datalines("ffffffffffff2b840846299108143414", 10, TS)
        assert 21.8 == d[0]["data"]["temprh_temp"]
        assert 35.0 == d[0]["data"]["temprh_rh"]
        assert 21.93 == d[0]["data"]["temp_out1"]
        assert 5.172 == d[0]["data"]["batt"]
        assert 4 == len(d[0]["data"])
        assert TS == d[0]["time"]

    def test_analog1_analog2_temp_in(self):
        d = sensornode.create_datalines("0d0016090028b30b143414", 21, TS)
        assert 0.013 == d[0]["data"]["analog1"]
        assert 0.009 == d[0]["data"]["analog2"]
        assert 29.95 == d[0]["data"]["temp_in"]
        assert 5.172 == d[0]["data"]["batt"]
        assert 4 == len(d[0]["data"])
        assert TS == d[0]["time"]

    def test_batt_temp_in_temp_out1(self):
        d = sensornode.create_datalines("8c14280b09297808", 20, TS)
        assert 5.260 == d[0]["data"]["batt"]
        assert 23.15 == d[0]["data"]["temp_in"]
        assert 21.68 == d[0]["data"]["temp_out1"]
        assert 3 == len(d[0]["data"])
        assert TS == d[0]["time"]


    def test_empty(self):
        d = sensornode.create_datalines("041528c22ea00000000000d72bc22ea000000000001a30c22ea0000000000000", 2, TS)
        assert d[0]["data"] == {}
        assert TS == d[0]["time"]


class TestPaxcounter:
    def test_wifi_ble(self):
        d = paxcounter.create_datalines("00020001", 1, TS)
        assert 2 == d[0]["data"]["wifi"]
        assert 1 == d[0]["data"]["ble"]
        assert TS == d[0]["time"]

    def test_wifi(self):
        d = paxcounter.create_datalines("0003", 1, TS)
        assert 3 == d[0]["data"]["wifi"]
        assert d[0]["data"].get("ble") is None
        assert TS == d[0]["time"]

    def test_time_request(self):
        d = paxcounter.create_datalines("ff", 9, TS)
        assert d[0]["data"] == {}

    def test_invalid_01(self):
        with pytest.raises(ValueError):
            paxcounter.create_datalines("fa117415aaaa", 1, TS)

    def test_invalid_02(self):
        with pytest.raises(ValueError):
            paxcounter.create_datalines("0d0016090028b30b143414", 21, TS)


class TestMilesight:
    def test_temp_hum(self):
        d = milesight.create_datalines("0367e70004684d", 85, TS)
        assert 23.1 == d[0]["data"]["temperature"]
        assert 38.5 == d[0]["data"]["humidity"]
        assert TS == d[0]["time"]

    def test_temp_hum_2(self):
        d = milesight.create_datalines("0367ed0004684b", 85, TS)
        assert 23.7 == d[0]["data"]["temperature"]
        assert 37.5 == d[0]["data"]["humidity"]
        assert TS == d[0]["time"]

    def test_temp_hum_3(self):
        d = milesight.create_datalines("0367f100046847", 85, TS)
        assert 24.1 == d[0]["data"]["temperature"]
        assert 35.5 == d[0]["data"]["humidity"]
        assert TS == d[0]["time"]

    def test_batt_temp_hum(self):
        d = milesight.create_datalines("0175640367f500046866", 85, TS)
        assert 100 == d[0]["data"]["battery"]
        assert 24.5 == d[0]["data"]["temperature"]
        assert 51.0 == d[0]["data"]["humidity"]
        assert TS == d[0]["time"]

    def test_batt_distance_position(self):
        d = milesight.create_datalines("01755C03824408040000", 85, TS)
        assert 92 == d[0]["data"]["battery"]
        assert 2116 == d[0]["data"]["distance"]
        assert 0 == d[0]["data"]["position"]
        assert TS == d[0]["time"]

    def test_batt_temp_distance_position(self):
        d = milesight.create_datalines("01755C0367010104824408050001", 85, TS)
        assert 92 == d[0]["data"]["battery"]
        assert 25.7 == d[0]["data"]["temperature"]
        assert 2116 == d[0]["data"]["distance"]
        assert 1 == d[0]["data"]["position"]
        assert TS == d[0]["time"]

    def test_temp_temp_abnormal_distance_distance_alarming(self):
        d = milesight.create_datalines("8367e800018482410601", 85, TS)
        assert 23.2 == d[0]["data"]["temperature"]
        assert 1 == d[0]["data"]["temperature_abnormal"]
        assert 1601 == d[0]["data"]["distance"]
        assert 1 == d[0]["data"]["distance_alarming"]
        assert TS == d[0]["time"]
