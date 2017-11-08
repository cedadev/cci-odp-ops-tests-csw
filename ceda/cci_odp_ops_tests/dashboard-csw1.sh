#!/bin/bash

output=$(curl -H "Content-type: application/xml" -s -w "curl_http_response=%{http_code}\n" -d '<?xml version="1.0" encoding="UTF-8"?><csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dct="http://purl.org/dc/terms/" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:geonet="http://www.fao.org/geonetwork" service="CSW" version="2.0.2" resultType="results" outputSchema="http://www.isotc211.org/2005/gmd" startPosition="1" maxRecords="300"><csw:Query typeNames="csw:Record"><csw:ElementSetName>full</csw:ElementSetName><csw:Constraint version="1.1.0"><ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>AnyText</ogc:PropertyName><ogc:Literal>%*%</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter></csw:Constraint></csw:Query></csw:GetRecords>' https://csw.ceda.ac.uk/geonetwork/srv/eng/csw-CEDA-CCI)

echo $output
response_s=$(echo $output | grep curl_http_response)
echo $reponse_s
echo $?

exit $?
