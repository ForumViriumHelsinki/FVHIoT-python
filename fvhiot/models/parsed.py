"""
Pydantic models for parsed data. 

Note that data may contain either 'time' field or 'start_time' and 'end_time' fields,
in addition to 'f'. The time fields should be mutually exclusive, i.e., the message
should contain only either 'time' field alone, or both, 'start_time' and 'end_time' 
fields, without 'time' being present. Currently this is handled via Union, which selects
the first Model that is present in the data or gives an error, if neither is.

TODO : warn/error both {'time'}  and {'start_time' and 'end_time'} are present in the data.
TODO : validate columns in header vs columns in 'f'

Sample data:
{
    "version": "1.0",
    "meta": {
      "timestamp_received": "2021-11-23T20:45:00.178866+00:00",
      "timestamp_parsed": "2021-11-23T20:45:00.288839Z",
    },
    "device": {
      "device_id": "B8A44F1F46E1",
      "state": "Production",
      …
    },
    "header": {
        "start_time": "2018-08-16T02:00:00.000Z",
        "end_time": "2018-08-16T02:20:43.000Z",
        "columns": {
            "0": {
                "name": "Temperature",
                "unit": "°C",  # or uri, or …
            },
          "1": {
                "name": "Humidity",
                "unit": "https://en.wikipedia.org/wiki/Humidity",
            },
        }
    },
    "data": [
        {
            "time": "2018-08-16T02:00:39.000Z",
            "f": { 
               "0": {"v": 3.0},
               "1": {"v": 30.0} 
             }
        },
        ...
        ]
"""


from typing import Any, Dict, List, Union

from device import Device

from pydantic import BaseModel, validator, Extra


class Column(BaseModel, extra=Extra.forbid):
    name: str
    unit: str


class Header(BaseModel, extra=Extra.forbid):
    start_time: str
    end_time: str
    columns: Dict[str, Column]


class Value(BaseModel, extra=Extra.forbid):
    v: Union[float, int, str]


class DataPointTime(BaseModel, extra=Extra.forbid):
    time: str
    f: Dict[str, Value]


class DataPointStartEndTime(BaseModel, extra=Extra.forbid):
    start_time: str
    end_time: str
    f: Dict[str, Value]


class ParsedData(BaseModel, extra=Extra.forbid):
    version: str = "1.0"
    meta: Dict[str, Any]
    device: Device
    header: Header
    data: List[Union[DataPointTime, DataPointStartEndTime]]

    @validator("data", pre=True)
    def check_time_fields(cls, list_vals: List[dict]) -> List[dict]:
        allowed_sets = set([frozenset(["time"]), frozenset(["start_time", "end_time"])])
        found_set = set()
        err_msg = "Data must contain time field combinations: ('time') XOR ('start_time' AND 'end_time')"
        for v in list_vals:
            if "time" in v:
                found_set.add("time")
            if "start_time" in v:
                found_set.add("start_time")
            if "end_time" in v:
                found_set.add("end_time")
            assert (
                found_set in allowed_sets
            ), f"Mutual exclusivity / missing field error. Found {list(found_set)} time fields. {err_msg}"
        return list_vals
