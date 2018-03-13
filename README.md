# MesoPy
[![Build Status](https://travis-ci.org/mesowx/MesoPy.svg?branch=master)](https://travis-ci.org/mesowx/MesoPy)
[![Coverage Status](https://coveralls.io/repos/mesowx/MesoPy/badge.svg?branch=master&service=github)](https://coveralls.io/github/mesowx/MesoPy?branch=master)
[![PyPI](https://img.shields.io/pypi/dm/MesoPy.svg)](https://pypi.python.org/pypi/MesoPy)

MesoPy is a small pure python wrapper around the MesoWest (http://mesowest.utah.edu/) API which is updated daily with over 4.5 million observations. It is useful for retrieving meteorological data at over 40,000 observation stations in the United States. This project was created with the researcher in mind and we would value feedback on how you are using MesoPy!

**Before using MesoPy, you will need to obtain an API key/token by filling out a quick form [here].** You will receive an email immediately with an API key and a link to generate a token. Click the link and copy the token you just generated when instancing the Meso object like so: `m = Meso(token='YOUR API_TOKEN')`

## Installation
There are two easy ways to install MesoPy:

1. Run  `pip install mesopy` from a command line window
2. Download the source folder and place `MesoPy.py` into your working directory

## Version 2 Updates
- The `requests` package dependency no longer exists
- Function names have been simplified
- Additional query parameters have been added to each function
- New functions added to request more services from MesoWest (data latency, statistics, network information)
- Lists may be passed to parameters

## Usage
#### Retrieving data:
You can request different types of observations by simply creating a Meso object and calling a function:

```
from MesoPy import Meso
m = Meso(token='YOUR API_TOKEN')
precip = m.precip(stid='kfnl', start='201504261800', end='201504271200', units='precip|in')
```

This returns the following data as a dictionary.
```json
{  
   "UNITS":{  
      "precipitation":"Inches"
   },
   "STATION":[  
      {  
         "STATUS":"ACTIVE",
         "MNET_ID":"1",
         "PERIOD_OF_RECORD":{  
            "start":"1970-01-01T00:00:00Z",
            "end":"2018-03-13T01:56:00Z"
         },
         "ELEVATION":"5016",
         "NAME":"Fort Collins\/Loveland - Northern Colorado Regional Airport",
         "RESTRICTED":false,
         "STID":"KFNL",
         "ELEV_DEM":"5000",
         "LONGITUDE":"-105.01667",
         "STATE":"CO",
         "OBSERVATIONS":{  
            "ob_start_time_1":"2015-04-26T18:15:00Z",
            "total_precip_value_1":0.09,
            "ob_end_time_1":"2015-04-27T11:55:00Z",
            "count_1":53
         },
         "LATITUDE":"40.45",
         "TIMEZONE":"America\/Denver",
         "ID":"192"
      }
   ],
   "SUMMARY":{  
      "DATA_QUERY_TIME":5.0201416016,
      "RESPONSE_CODE":1,
      "RESPONSE_MESSAGE":"OK",
      "METADATA_RESPONSE_TIME":"0.0920295715332 ms",
      "NUMBER_OF_OBJECTS":1,
      "PRECIP_DATA_TIME":5.4969787598,
      "DATA_PARSE_TIME":0.4601478577
   }
}
```

You can retrieve any of the dictionary keys/values listed above by merely doing the following:

```
# Let's print the total precip accumulation for Fort Collins Airport.
station = precip['STATION'][0]['STID'] # remember we stored the dictionary in the precip variable
totalPrecip =  precip['STATION'][0]['OBSERVATIONS']['total_precip_value_1'] 
print('The total accumulated precip at ' + station + ' was ' + str(totalPrecip) + '"')
```
Which prints:

> The total accumulated precip at KFNL was 0.09"

#####You should note one thing from the above example: 
Whenever the data you're requesting returns `['STATION']`, it is necessary to specify which station (index value) in the list you will subsequently be referring to. For example if you pass in `stid=kden,kslc`, the dictionary will return a list of the two stations' relevant info. So to get to information on KDEN (Denver), you would type `['STATION'][0]` because KDEN would be first in the list of stations and `['STATION'][1]` for KSLC (Salt Lake City). Remember that `{}` specifies a dictionary and `[]` denotes a list and `[0]` is the first position in a list. It may be useful to store `precip['STATION'][i]` as a variable to reduce clutter. For example, `Denver_PrecipObs = precip['STATION'][0]`  and `SaltLake_PrecipObs = precip['STATION'][1]`. Then, you could write `print(Denver_PrecipObs['OBSERVATIONS']['total_precip_value_1'])` which returns `0.13` (for the above request). The API was created to always return a list (since a user can request multiple stations at any time) so this will always be a stipulation. 

#### Function List:
1. `latest()` -  Get the latest observation data for a particular station(s)
2. `attime()` - Get the latest observation data for a particular station(s) at a specific time
3. `precipitation()` - Obtain precip totals over a specified period for a station(s)
4. `timeseries()` - Retrieve observations over a specified period for a station(s)
5. `climatology()` - Obtain a climatology over a specified period for a station(s)
6. `metadata()` - Retrieve a list of station metadata based on search parameters
7. `variables()` - Get a list of sensor variables possible for observing stations
8. `climate_stats()` - Retrieve aggregated yearly climate statistics for a station(s)
9. `time_stats()` - Obtain statistics for a specific time frame for a station(s)
10. `latency()` - Retrieve data latency values for a station(s)
11. `networks()` - Obtain metadata concerning the observing networks in the MesoWest repository
12. `networktypes()` - Returns the network categories for the observing networks

## Documentation
Each function is **well** documented in the docstrings. In an interactive interpreter, simply type `help(SOME_FUNC)` or in your code, type `SOME_FUNC.__doc__` 

## Example Projects 
These can be found in the `/examples` path.

## Version and License
2.0.2 released on 7 Jan 2016 under the MIT license

## Support and Credits
MesoPy was designed to be as simple as possible and we hope you enjoy its usage. If you have any questions/comments, please direct them to support@mesowest.org. The [MesoWest group] is led by  Dr. John Horel at the University of Utah. Additional facilities were provided by the [Western Region] of the National Weather Service. 

[requests]:https://pypi.python.org/pypi/requests/
[here]: http://mesowest.org/api/signup/
[MesoWest group]: http://meso1.chpc.utah.edu/mesowest_overview/
[Western Region]: http://www.wrh.noaa.gov/
