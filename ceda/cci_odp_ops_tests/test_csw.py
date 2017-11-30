#!/usr/bin/env python
"""Test CCI Open Data Portal CSW service
"""
__author__ = "P J Kershaw"
__date__ = "07/11/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import unittest
import xml.etree.ElementTree as ET

import requests


class CSWTestCase(unittest.TestCase):
    '''Unit test case for testing ESA CCI Open Data Portal CSW'''

    CSW_URI = 'https://csw.ceda.ac.uk/geonetwork/srv/eng/csw-CEDA-CCI'
    DASHBOARD_CSW_QUERY_HDR = {"Content-type": "application/xml"}
    DASHBOARD_CSW_QUERY_BODY = '''<?xml version="1.0" encoding="UTF-8"?>
<csw:GetRecords
    xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dct="http://purl.org/dc/terms/"
    xmlns:gmd="http://www.isotc211.org/2005/gmd"
    xmlns:gco="http://www.isotc211.org/2005/gco"
    xmlns:geonet="http://www.fao.org/geonetwork"
    service="CSW"
    version="2.0.2"
    resultType="results"
    outputSchema="http://www.isotc211.org/2005/gmd"
    startPosition="1"
    maxRecords="300">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>full</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
        <ogc:Filter>
             <ogc:PropertyIsEqualTo>
                 <ogc:PropertyName>AnyText</ogc:PropertyName>
                 <ogc:Literal>%*%</ogc:Literal>
             </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
'''

    GMD_NS_URI = "http://www.isotc211.org/2005/gmd"
    GML_NS_URI = "http://www.opengis.net/gml/3.2"
    GCO_NS_URI = "http://www.isotc211.org/2005/gco"

    GET_RECS_RESP_TAG = ('{http://www.opengis.net/cat/csw/2.0.2}'
                         'GetRecordsResponse')

    def _csw_query(self, csw_uri, post_query, headers):
        response = requests.post(csw_uri, data=post_query, headers=headers)

        resp_elem = ET.fromstring(response.text)

        return response.status_code, resp_elem

    def test01_csw_dashboard_query(self):
        status_code, resp_elem = self._csw_query(self.__class__.CSW_URI,
                                     self.__class__.DASHBOARD_CSW_QUERY_BODY,
                                     self.__class__.DASHBOARD_CSW_QUERY_HDR)
        self.assertEqual(status_code, 200, msg="Expecting 200 OK response code")
        self.assertEqual(resp_elem.tag, self.__class__.GET_RECS_RESP_TAG,
                         msg="Expecting {} tag in response for {!r}".format(
                               self.__class__.GET_RECS_RESP_TAG,
                               self.__class__.CSW_URI))

    def test02_csw_dashboard_check_temporal_extent(self):
        status_code, resp_elem = self._csw_query(self.__class__.CSW_URI,
                                     self.__class__.DASHBOARD_CSW_QUERY_BODY,
                                     self.__class__.DASHBOARD_CSW_QUERY_HDR)
        self.assertEqual(status_code, 200,
                         msg="Expecting 200 OK response code for {!r}".format(
                             self.__class__.CSW_URI))

        temporal_start_time = resp_elem.findall(
            ".//{%s}TimePeriod/{%s}beginPosition"
            % (2*(self.__class__.GML_NS_URI,)))

        self.assertGreater(len(temporal_start_time), 0,
                           msg="No temporal start elements found for "
                            "{!r}".format(self.__class__.CSW_URI))

        temporal_end_time = resp_elem.findall(
            ".//{%s}TimePeriod/{%s}endPosition"
            % (2*(self.__class__.GML_NS_URI,)))

        self.assertGreater(len(temporal_end_time), 0,
                        msg="No temporal end elements found for {!r}".format(
                        "self.__class__.CSW_URI"))


    def test03_csw_dashboard_check_geographic_extent(self):
        status_code, resp_elem = self._csw_query(self.__class__.CSW_URI,
                                     self.__class__.DASHBOARD_CSW_QUERY_BODY,
                                     self.__class__.DASHBOARD_CSW_QUERY_HDR)
        self.assertEqual(status_code, 200,
                         msg="Expecting 200 OK response code for {!r}".format(
                             self.__class__.CSW_URI))

        west_bound_lon = resp_elem.findall(
            ".//{%s}geographicElement"
            "/{%s}EX_GeographicBoundingBox"
            "/{%s}westBoundLongitude"
            "/{%s}Decimal"
            % (3*(self.__class__.GMD_NS_URI,) + (self.__class__.GCO_NS_URI,)))

        self.assertGreater(len(west_bound_lon), 0,
                           msg="No West Bound Longitude elements found in "
                           "response {!r}".format(self.__class__.CSW_URI))

        south_bound_lat = resp_elem.findall(
            ".//{%s}geographicElement"
            "/{%s}EX_GeographicBoundingBox"
            "/{%s}southBoundLatitude"
            "/{%s}Decimal"
            % (3*(self.__class__.GMD_NS_URI,) + (self.__class__.GCO_NS_URI,)))

        self.assertGreater(len(south_bound_lat), 0,
                        msg="No South Bound Latitude elements found in "
                        "response {!r}".format(self.__class__.CSW_URI))

