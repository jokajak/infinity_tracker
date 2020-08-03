#!/usr/bin/env python
# Utility functions for infinity tracker.
import json
import urllib2
import urlparse

from six import binary_type, integer_types, text_type


# From python-influxdb
def _get_unicode(data, force=False):
    """Try to return a text aka unicode object from the given data."""
    if isinstance(data, binary_type):
        return data.decode("utf-8")
    elif data is None:
        return ""
    elif force:
        return str(data)
    else:
        return data


# From python-influxdb
def _escape_tag(tag):
    tag = _get_unicode(tag, force=True)
    return (
        tag.replace("\\", "\\\\")
        .replace(" ", "\\ ")
        .replace(",", "\\,")
        .replace("=", "\\=")
    )


# From python-influxdb
def _escape_value(value):
    value = _get_unicode(value)
    if isinstance(value, text_type) and value != "":
        return '"{0}"'.format(value.replace('"', '\\"').replace("\n", "\\n"))
    elif isinstance(value, integer_types) and not isinstance(value, bool):
        return str(value) + "i"
    else:
        return str(value)


def extract_req_body(s):
    qsl = urlparse.parse_qsl(s, keep_blank_values=True)
    for k, v in qsl:
        if k == "data":
            return v
    return ""


def get_current_temp(api_key, location_query):
    if not (api_key and location_query):
        return False
    base_url = "http://api.wunderground.com/api/{}/".format(api_key)
    url = "{}/geolookup/conditions/q/{}.json".format(base_url, location_query)
    f = urllib2.urlopen(url)
    json_string = f.read()
    parsed_json = json.loads(json_string)
    temp_f = parsed_json["current_observation"]["temp_f"]
    f.close()
    return temp_f
