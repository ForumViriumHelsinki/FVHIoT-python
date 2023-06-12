# FVHIoT parsers

This module contains parsers, which usually take in some
hex string and return the parsed data in an object in
"well-known-parsed-data-format". 

All modules must implement `create_datalines()` function
and it must return a list of objects having
("time" | ("starttime" & "endtime") & "data") keys

See parsers source code to see how they are implemented and 
run them (with or without input) to see what they return.  

E.g. calling 

`sensornode.create_datalines("01e32337f80e14941228ba01295701", 10)`

should return an object like this:

```
[
  {
    "time": "2022-03-02T12:21:30.123000+00:00",
    "data": {
      "lat": 60.2079488,
      "lon": 25.1148032,
      "batt": 4.756,
      "temp_in": 4.42
    }
  }
]
```