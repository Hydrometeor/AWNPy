# ==================================================================================================================== #
# MesoPy                                                                                                               #
# Version: 2.0.0                                                                                                       #
# Copyright (c) 2015-17 MesoWest Developers <atmos-mesowest@lists.utah.edu>
#           (c) 2020 AgWeatherNet <joe.zagrodnik@wsu.edu>
#
#                                                                                                                      #
# LICENSE:                                                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated         #
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the  #
# rights to use,copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to       #
# permit persons to whom the Software is furnished to do so, subject to the following conditions:                      #
#                                                                                                                      #
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the #
# Software.                                                                                                            #
#                                                                                                                      #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE #
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS   #
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,WHETHER IN AN ACTION OF CONTRACT, TORT OR   #
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.     #
#                                                                                                                      #
# ==================================================================================================================== #

try:
    import pandas as pd
except ImportWarning:
    print('Pandas not installed -- unable to return API calls as dataframes')
try:
    import urllib.parse
    import urllib.request
    import urllib.error
except ImportError:
    import urllib2
    import urllib

import json
import datetime
import pandas as pd
import pdb

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


# ==================================================================================================================== #
# AWNPyError class                                                                                                    #
# Type: Exception                                                                                                      #
# Description: This class is simply the means for error handling when an exception is raised.                          #
# ==================================================================================================================== #


class AWNPyError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        r""" This just returns one of the error messages listed in the checkresponse() function"""
        return repr(self.error_message)


# ==================================================================================================================== #
# AWN class                                                                                                           #
# Type: Main                                                                                                           #
# Description: This class defines an instance of AWNPy and takes in the user's token                                  #
# ==================================================================================================================== #


class AWN(object):
    def __init__(self, username, password):
        r""" Instantiates an instance of AWNPy.

        Arguments:
        ----------
        token: string, mandatory
            Your API token that authenticates you for requests against AWN.mes

        Returns:
        --------
            None.

        Raises:
        -------
            None.
        """

        self.base_url = 'https://weather.wsu.edu/webservice/'
        #self.base_url = 'http://weather.prosser.wsu.edu/webservice/'
        self.username = username
        self.password = password
        self.geo_criteria = ['stid', 'state', 'country', 'county', 'radius', 'bbox', 'cwa', 'nwsfirezone', 'gacc',
                             'subgacc']

    # ================================================================================================================ #
    # Functions:                                                                                                       #
    # ================================================================================================================ #

    @staticmethod
    def _checkresponse(response):
        r""" Returns the data requested by the other methods assuming the response from the API is ok. If not, provides
        error handling for all possible API errors. HTTP errors are handled in the get_response() function.

        Arguments:
        ----------
            None.

        Returns:
        --------
            The response from the API as a dictionary if response['message'] exists.

        Raises:
        -------
            AWNPyError: Gives different response messages depending on returned code from API. A code of -1 is for
            invalid authentication. A code of 1 with no data means no results matched query.

        """

        results_error = 'No results were found matching your query'
        auth_error = 'Username/password not valid, please contact weather@wsu.edu to ' \
                     'resolve this'
        #rule_error = 'This request violates a rule of the API. Please check the guidelines for formatting a data ' \
        #             'request and try again'
        catch_error = 'Something unexpected happened. Check all your calls and try again'


        if response['status'] == 1:
            try:
                response['message']
                return response
            except:
                raise AWNPyError(results_error)
        elif response['status'] == -1:
            raise AWNPyError(auth_error)
        else:
            raise AWNPyError(catch_error)

    def _get_response(self, endpoint, request_dict):
        """ Returns a dictionary of data requested by each function.

        Arguments:
        ----------
        endpoint: string, mandatory
            Set in all other methods, this is the API endpoint specific to each function.
        request_dict: string, mandatory
            A dictionary of parameters that are formatted into the API call.

        Returns:
        --------
            response: A dictionary that has been dumped from JSON.

        Raises:
        -------
            AWNPyError: Overrides the exceptions given in the requests library to give more custom error messages.
            Connection_error occurs if no internet connection exists. Timeout_error occurs if the request takes too
            long and redirect_error is shown if the url is formatted incorrectly.

        """
        http_error = 'Could not connect to the API. This could be because you have no internet connection, a parameter' \
                     ' was input incorrectly, or the API is currently down. Please try again.'
                     
        json_error = 'Could not retrieve JSON values. Try again with a shorter date range.'

        # For python 3.4
        try:
            qsp = urllib.parse.urlencode(request_dict, doseq=True)
            resp = urllib.request.urlopen(self.base_url + endpoint + '/?' + qsp).read()
        # For python 2.7
        except AttributeError or NameError:
            try:
                qsp = urllib.urlencode(request_dict, doseq=True)
                resp = urllib2.urlopen(self.base_url + endpoint + '?' + qsp).read()
            except urllib2.URLError:
                raise AWNPyError(http_error)
        except urllib.error.URLError:
            raise AWNPyError(http_error)
        try:
            json_data = json.loads(resp.decode('utf-8'))
        except ValueError:
            raise AWNPyError(json_error)

        return self._checkresponse(json_data)

    def _check_geo_param(self, arg_list):
        r""" Checks each function call to make sure that the user has provided at least one of the following geographic
        parameters: 'stid', 'state', 'country', 'county', 'radius', 'bbox', 'cwa', 'nwsfirezone', 'gacc', or 'subgacc'.

        MIGHT WANT TO REWRITE THIS TO CHECK RESPONSES?

        Arguments:
        ----------
        arg_list: list, mandatory
            A list of kwargs from other functions.

        Returns:
        --------
            None.

        Raises:
        -------
            AWNPyError if no geographic search criteria is provided.

        """

        geo_func = lambda a, b: any(i in b for i in a)
        check = geo_func(self.geo_criteria, arg_list)
        if check is False:
            raise AWNPyError('No stations or geographic search criteria specified. Please provide one of the '
                              'following: stid, state, county, country, radius, bbox, cwa, nwsfirezone, gacc, subgacc')


    def _station_name_to_station_id(self, kwargs):
        """
        If a station name is provided instead of an ID, this function converts the STATION_NAME to STATION_ID.

        Arguments:
        kwargs: args from a call to stationdata(), including a STATION_NAME argument
        Returns:
        kwargs with a STATION_ID specified
        """

        metadata = self.metadata(return_dataframe=True)
        if kwargs['STATION_NAME'] not in metadata['STATION_NAME'].values:
            raise ValueError('STATION_NAME is not in list of AgWeatherNet stations')
        station_id = metadata.loc[metadata['STATION_NAME'][metadata['STATION_NAME'] ==
                                                           kwargs['STATION_NAME']].index[0]]['STATION_ID']
        kwargs['STATION_ID'] = station_id
        kwargs.pop('STATION_NAME', None)
        return kwargs


    def metadata(self, return_dataframe=False, **kwargs):
        r""" Returns the metadata for a station or stations. Specifying no kwargs will return metadata for all stations.
        See below for optional parameters.

        Arguments:
        return_dataframe: bool, optional
            If true, return results as a Pandas Dataframe. If false, return results as a dict.
        ----------
        STATION_ID: string, optional
            You may supply a single station id value if you would like metadata for a specific station.
        INSTALLATION_DATE: string, optional
            If supplied, only stations installed before the date will be returned.
            Dates should be in YYYYmmdd format.
        STATE: string (2 character abbreviation), optional
            If supplied, only stations that match the two character state abbreviation will be returned.
        COUNTY: string, optional
            If supplied, only stations that match the county will be returned.
        AT: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have an air
            temperature sensor (Y=Yes, N=No).
        RH: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a relative
            humidity sensor (Y=Yes, N=No).
        P: string, optional
            If supplied, valid values are “Y” or “N”. Stations will be filtered on whether or not they have a
            precipitation sensor (Y=Yes, N=No).
        WS: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a wind
            speed sensor (Y=Yes, N=No).
        WD: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a wind
            direction sensor (Y=Yes, N=No).
        LW: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a leaf
            wetness sensor (Y=Yes, N=No).
        SR: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a
            solar radiation sensor (Y=Yes, N=No).
        ST2: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will befiltered on whether or not they have a soil
            temperature sensor at 2 inch depth (Y=Yes, N=No).
        ST8: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a soil
            temperature sensor at 8 inch depth (Y=Yes, N=No).
        SM8: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a soil
             moisture sensor at 8 inch depth (Y=Yes, N=No).
        MSLP: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have an air
             pressure sensor (Y=Yes, N=No).

        Returns:
        --------
        A pandas dataframe of metadata containing the following:
        STATE: The 2 letter abbreviation of the state (political entity) where the weather station resides.
        COUNTY: The county (secondary political entity) where the the weather station resides.
        CITY: The nearest identified population center to the station, if available.  This may be null or an empty
            string.
        ZIPCODE: The zip code where the weather station resides, if available. This may be null or an empty string.
        LATITUDE_DEGREE: The latitude of the physical location of the weather station, in degrees
        LONGITUDE_DEGREE: The longitude of the physical location of the weather station, in degrees.
        ELEVATION_FEET: The elevation compared to sea level of the base of the weather station.
        INSTALLATION_DATE: The installation date of the weather station.  Data is available from the installation date
            through present.  The installation date is returned in YYYY-mm-dd format.
        STATION_ID: The unique station identifier assigned by the AgWeatherNet program to the weather station.
        STATION_NAME: The current common name of the weather station.  This may change without notice and is intended
            as a friendly reference to the station.
        OLD_LONG_NAME: The old name of the weather station if it was changed.
        STATION_SPONSOR: Acknowledgements of support or contributions to the location, installation or maintenance of
            a weather station
        TIER: Station tier (1, 2, or 3). See weather.wsu.edu for details.
        AT_F: If the weather station has an air temperature sensor installed that reports in Degrees Fahrenheit, then
            the value will be Y.  If no sensor is installed, then the value will be N.
        RH_PCNT: If the weather station has a relative humidity sensor installed that reports in Percent, then the
            value will be Y.  If no sensor is installed, then the value will be N.
        P_INCHES: If the weather station has a precipitation sensor installed that reports in Inches, then the value
            will be Y.  If no sensor is installed, then the value will be N.
        WS_MPH: If the weather station has a wind speed sensor installed that reports in Miles Per Hour, then the value
            will be Y.  If no sensor is installed, then the value will be N.
        WD_DEGREE: If the weather station has a wind direction sensor installed that reports in Compass Degrees, then
            the value will be Y.  If no sensor is installed, then the value will be N.
        LW_UNITIY: If the weather station has a leaf wetness sensor installed that reports in Unity (values between 0
            and 1, 0.4 considered wet), then the value will be Y.  If no sensor is installed, then the value will be N.
        SR_WM2: If the weather station has a solarradiation sensor installed that reports in Watts per Meter Squared,
            then the value will be Y.  If no sensor is installed, then the value will be N.
        ST2_F: If the weather station has a soil temperature sensor installed at a 2 inch depth that reports in Degrees
            Fahrenheit, then the value will be Y.  If no sensor is installed, then the value will be N.
        ST8_F: If the weather station has a soil temperature sensor installed at a 8 inch depth that reports in Degrees
            Fahrenheit, then the value willbe Y.  If no sensor is installed, then the value will be N.
        STM8_PCNT: If the weather station has a soil moisture sensor installed at a8 inch depth that reports in Percent
            Volumetric Water Content, then the value will be Y.  If no sensor is installed, then the value will be N.
        MSLP_HPA: If the weather station has a barometric pressure sensor installed that reports in HPA (hecto pascals),
            then the value will be Y.  If no sensor is installed, then the value will be N.

        Raises:
        -------
            None.

        """

        #self._check_geo_param(kwargs)
        kwargs['uname'] = self.username
        kwargs['pass'] = self.password

        response_data = self._get_response('metadata', kwargs)
        if return_dataframe:
            return pd.DataFrame.from_dict(response_data['message'])
        else:
            return response_data['message']

    def stationdata(self, return_dataframe=False, **kwargs):
        r""" Returns station data station or stations. Specifying no kwargs will return data for all stations.
        See below for optional parameters.

        Arguments:
        return_dataframe: bool, optional
            If true, return results as a Pandas Dataframe. If false, return results as a dict.
        ----------
        STATION_ID: string, optional
            You may supply a single station id value if you would like metadata for a specific station.
        INSTALLATION_DATE: string, optional
            If supplied, only stations installed before the date will be returned.
            Dates should be in YYYYmmdd format.
        STATE: string (2 character abbreviation), optional
            If supplied, only stations that match the two character state abbreviation will be returned.
        COUNTY: string, optional
            If supplied, only stations that match the county will be returned.
        AT: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have an air
            temperature sensor (Y=Yes, N=No).
        RH: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a relative
            humidity sensor (Y=Yes, N=No).
        P: string, optional
            If supplied, valid values are “Y” or “N”. Stations will be filtered on whether or not they have a
            precipitation sensor (Y=Yes, N=No).
        WS: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a wind
            speed sensor (Y=Yes, N=No).
        WD: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a wind
            direction sensor (Y=Yes, N=No).
        LW: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a leaf
            wetness sensor (Y=Yes, N=No).
        SR: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a
            solar radiation sensor (Y=Yes, N=No).
        ST2: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will befiltered on whether or not they have a soil
            temperature sensor at 2 inch depth (Y=Yes, N=No).
        ST8: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a soil
            temperature sensor at 8 inch depth (Y=Yes, N=No).
        SM8: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have a soil
             moisture sensor at 8 inch depth (Y=Yes, N=No).
        MSLP: string, optional
            If supplied, valid values are “Y” or “N”.  Stations will be filtered on whether or not they have an air
             pressure sensor (Y=Yes, N=No).

        Returns:
        --------
        A pandas dataframe of metadata containing the following:
        STATE: The 2 letter abbreviation of the state (political entity) where the weather station resides.
        COUNTY: The county (secondary political entity) where the the weather station resides.
        CITY: The nearest identified population center to the station, if available.  This may be null or an empty
            string.
        ZIPCODE: The zip code where the weather station resides, if available. This may be null or an empty string.
        LATITUDE_DEGREE: The latitude of the physical location of the weather station, in degrees
        LONGITUDE_DEGREE: The longitude of the physical location of the weather station, in degrees.
        ELEVATION_FEET: The elevation compared to sea level of the base of the weather station.
        INSTALLATION_DATE: The installation date of the weather station.  Data is available from the installation date
            through present.  The installation date is returned in YYYY-mm-dd format.
        STATION_ID: The unique station identifier assigned by the AgWeatherNet program to the weather station.
        STATION_NAME: The current common name of the weather station.  This may change without notice and is intended
            as a friendly reference to the station.
        OLD_LONG_NAME: The old name of the weather station if it was changed.
        STATION_SPONSOR: Acknowledgements of support or contributions to the location, installation or maintenance of
            a weather station
        TIER: Station tier (1, 2, or 3). See weather.wsu.edu for details.
        AT_F: If the weather station has an air temperature sensor installed that reports in Degrees Fahrenheit, then
            the value will be Y.  If no sensor is installed, then the value will be N.
        RH_PCNT: If the weather station has a relative humidity sensor installed that reports in Percent, then the
            value will be Y.  If no sensor is installed, then the value will be N.
        P_INCHES: If the weather station has a precipitation sensor installed that reports in Inches, then the value
            will be Y.  If no sensor is installed, then the value will be N.
        WS_MPH: If the weather station has a wind speed sensor installed that reports in Miles Per Hour, then the value
            will be Y.  If no sensor is installed, then the value will be N.
        WD_DEGREE: If the weather station has a wind direction sensor installed that reports in Compass Degrees, then
            the value will be Y.  If no sensor is installed, then the value will be N.
        LW_UNITIY: If the weather station has a leaf wetness sensor installed that reports in Unity (values between 0
            and 1, 0.4 considered wet), then the value will be Y.  If no sensor is installed, then the value will be N.
        SR_WM2: If the weather station has a solarradiation sensor installed that reports in Watts per Meter Squared,
            then the value will be Y.  If no sensor is installed, then the value will be N.
        ST2_F: If the weather station has a soil temperature sensor installed at a 2 inch depth that reports in Degrees
            Fahrenheit, then the value will be Y.  If no sensor is installed, then the value will be N.
        ST8_F: If the weather station has a soil temperature sensor installed at a 8 inch depth that reports in Degrees
            Fahrenheit, then the value willbe Y.  If no sensor is installed, then the value will be N.
        STM8_PCNT: If the weather station has a soil moisture sensor installed at a8 inch depth that reports in Percent
            Volumetric Water Content, then the value will be Y.  If no sensor is installed, then the value will be N.
        MSLP_HPA: If the weather station has a barometric pressure sensor installed that reports in HPA (hecto pascals),
            then the value will be Y.  If no sensor is installed, then the value will be N.

        Raises:
        -------
            None.

        """

        kwargs['uname'] = self.username
        kwargs['pass'] = self.password
        # convert datetimes to strings that the API can read
        #self._datetime_to_string(kwargs)
        # if STATION_NAME specified, convert to STATION_ID
        if 'STATION_NAME' in kwargs:
            kwargs = self._station_name_to_station_id(kwargs)

        response_data = self._get_response('stationdata', kwargs)
        pdb.set_trace()

        pd.DataFrame.from_dict(response_data['message'])

        pd.DataFrame.from_dict(response_data['message'][0]['DATA'])

        pdb.set_trace()



        return

    def _stationdata_to_dataframe(self, response):
        """
        helper function to convert station data into a pandas dataframe
        :param response: the response to a
        :return:
        """

