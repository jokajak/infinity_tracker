#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This proxies connections for a Carrier Infinity system.
# It reads the data being transferred and logs it to an influxdb server
import argparse
import json
import logging
import proxy
import re
import requests
import urllib2
import urlparse
import xml.etree.ElementTree as ET

from utils import _escape_tag, _escape_value, extract_req_body

logger = logging.getLogger()
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# global for passing influxdb URL
influxdb = None

# global for passing wunderground api key and location
api_key = None
location_query = None


# Registration of routes
routes = {
    'save': {},
    'request': {},
    'response': {}
}


def route(rule, f_type='save'):
    """A decorator that is used to register a view function for a
    given URL rule.

    f_type allows specifying whether it handles a request, a response,
    or a save
    """
    def decorator(f):
        routes[f_type][rule] = f
        return f
    return decorator


def get_current_temp(api_key, location_query):
    if not (api_key and location_query):
        return False
    url = 'http://api.wunderground.com/api/{}/geolookup/conditions/q/{}.json'
    url = url.format(api_key, location_query)
    f = urllib2.urlopen(url)
    json_string = f.read()
    parsed_json = json.loads(json_string)
    temp_f = parsed_json['current_observation']['temp_f']
    f.close()
    return temp_f


def status_handler(update_text, sn='Unknown'):
    if not influxdb:
        return
    try:
        root = ET.fromstring(update_text)
    except Exception as e:  # NOQA
        logger.exception('Failed to parse request: %s',
                         update_text)
        return
    sn = _escape_tag(sn)
    lines = []
    value = _escape_value(float(root.find('filtrlvl').text))
    lines.append('filter,sn={} value={}'.format(sn, value))
    unit_mode = _escape_value(root.find('mode').text)
    lines.append('mode,sn={} value={}'.format(sn, unit_mode))
    zones = []
    known_tags = {
        'enabled': None,
        'currentActivity': 'activity',
        'rt': 'temp',
        'rh': 'humidity',
        'fan': 'fan',
        'htsp': 'heat_set_point',
        'clsp': 'cool_set_point',
        'hold': 'hold',
        'name': None,
        'otmr': None,
    }
    transforms = {
        'temp': float,
        'humidity': float,
        'heat_set_point': float,
        'cool_set_point': float,
        'fan': lambda val: val != 'off',  # Converts to boolean
        'hold': lambda val: val != 'off'  # Converts to boolean
    }

    for zone_set in root.findall('zones'):
        for zone in zone_set.findall('zone'):
            if zone.find('enabled').text == 'off':
                continue
            hvac_zone = {
                'zone_id': _escape_tag(zone.attrib['id']),
                'name': _escape_tag(zone.find('name').text),
                'attributes': {}
            }
            for tag, key in known_tags.items():
                node = zone.find(tag)
                if node is None:
                    logger.debug('Could not find tag %s in body: %s', tag,
                                 zone.find(tag))
                    continue
                value = node.text or '0'
                transform = transforms.get(key, str)
                value = transform(value)
                hvac_zone['attributes'][key] = _escape_value(value)
            zones.append(hvac_zone)
            for child in zone:
                if child.tag not in known_tags:
                    logger.info('Unknown tag: %s: %s', child.tag, child.text)
    for zone in zones:
        templ = 'sn={},zone={},zone_id={}'.format(sn, zone['name'],
                                                  zone['zone_id'])
        for field, value in zone['attributes'].items():
            if not field:
                continue
            if isinstance(value, float):
                line = '{},{} value={}'.format(field, templ, value)
            else:
                line = '{},{} value={}'.format(field, templ, value)
            lines.append(line)
        logger.debug(unit_mode)
        logger.debug(unit_mode == '"cool"')
        if unit_mode == '"cool"' or unit_mode == '"dehumidify"':
            logger.debug('Cooling')
            field = 'cooling'
            value = zone['attributes']['temp']
            line = '{},{} value={}'.format(field, templ, value)
            lines.append(line)
        if unit_mode == '"heat"':
            field = 'heating'
            value = zone['attributes']['temp']
            line = '{},{} value={}'.format(field, templ, value)
            lines.append(line)

    headers = {
        'Content-Type': 'application/octet-stream',
        'Accept': 'text/plain'
    }
    try:
        temp_f = get_current_temp(api_key, location_query)
        if temp_f:
            lines.append('outside_temp,sn={} value={}'.format(sn, temp_f))
    except Exception as e:
        logger.exception('Failed to get current temp: %s', e)
    lines = '\n'.join(lines)
    lines = lines + '\n'
    # logger.debug('Submitting %s', lines)
    r = requests.post(influxdb, headers=headers, data=lines)
    logging.getLogger('requests').debug(r.text)
    return


@route('/systems/(?P<sn>.*)/status', 'request')
def systems_status_req_handler(req, req_body, sn):
    """Handle save requests for systems status."""
    content_length = req.headers.get('Content-Length', '')
    if content_length == 0:
        logger.debug('Status check')
    else:
        req_body_text = None
        content_type = req.headers.get('Content-Type', '')
        if content_type.startswith('application/x-www-form-urlencoded'):
            if req_body is not None:
                req_body_text = extract_req_body(req_body)
                status_handler(req_body_text, sn)


@route('/systems/(?P<sn>.*)/status')
def systems_status_save_handler(req, req_body, res, res_body, sn):
    """Handle save requests for systems status."""
    content_type = res.headers.get('Content-Type', '')

    if content_type.startswith('application/xml'):
        try:
            root = ET.fromstring(res_body)
            server_has_changes = root.find('serverHasChanges').text
            if server_has_changes != 'false':
                logger.debug('Remote changes')
            else:
                logger.debug('No remote changes')
        except Exception as e:  # NOQA
            logger.exception('Failed to parse response: %s', res_body)
    return True


@route('/systems/(?P<sn>.*)')
def config_handler(req, req_body, res, res_body, sn):
    """Handle system config updates."""
    logger.info('System config update')
    return True


@route('/systems/(?P<sn>.*)/idu_config')
def idu_config_handler(req, req_body, res, res_body, sn):
    """Handle InDoor Unit config updates."""
    logger.info('InDoor Unit config update')
    pass


@route('/systems/(?P<sn>.*)/odu_config')
def odu_config_handler(req, req_body, res, res_body, sn):
    """Handle OutDoor Unit config updates."""
    logger.info('OutDoor Unit config update')
    pass


@route('/systems/(?P<sn>.*)/idu_status')
def idu_status_handler(req, req_body, res, res_body, sn):
    """Handle InDoor Unit status updates."""
    logger.info('InDoor Unit status update')
    pass


@route('/systems/(?P<sn>.*)/odu_status')
def odu_status_handler(req, req_body, res, res_body, sn):
    """Handle OutDoor Unit status updates."""
    logger.info('OutDoor Unit status update')
    pass


@route('/Alive')
def alive_handler(req, req_body, res, res_body):
    """Handles Alive calls."""
    logger.info('Alive called')
    return True


@route('/weather/(?P<zip>.*)/forecast')
def forecast_handler(req, req_body, res, res_body, zip):
    """Handles forecast requests"""
    return True


class CarrierProxyRequestHandler(proxy.ProxyRequestHandler):
    def request_handler(self, req, req_body):
        """Used to modify requests."""
        u = urlparse.urlsplit(req.path)
        path = u.path
        handler = None
        handler_routes = routes['request']
        for route in handler_routes:
            route_re = '^{}$'.format(route)  # Find exact matches only
            m = re.match(route_re, path)
            if m:
                handler = handler_routes[route]
                # From https://stackoverflow.com/q/11065419
                # Convert match elements to kw args
                handler(req, req_body, **m.groupdict())
        pass

    def response_handler(self, req, req_body, res, res_body):
        """Used to modify responses."""
        u = urlparse.urlsplit(req.path)
        path = u.path
        handler = None
        handler_routes = routes['response']
        for route in handler_routes:
            route_re = '^{}$'.format(route)  # Find exact matches only
            m = re.match(route_re, path)
            if m:
                handler = handler_routes[route]
                # From https://stackoverflow.com/q/11065419
                # Convert match elements to kw args
                handler(req, req_body, res, res_body, **m.groupdict())
        pass

    def save_handler(self, req, req_body, res, res_body):
        squelch_output = False
        u = urlparse.urlsplit(req.path)
        path = u.path
        handler = None
        handler_routes = routes['save']
        for route in handler_routes:
            route_re = '^{}$'.format(route)  # Find exact matches only
            m = re.match(route_re, path)
            if m:
                logger.debug('Found a save handler for %s', path)
                handler = handler_routes[route]
                # From https://stackoverflow.com/q/11065419
                # Convert match elements to kw args
                squelch_output = handler(req, req_body, res, res_body,
                                         **m.groupdict())
        if not squelch_output:
            self.print_info(req, req_body, res, res_body)
        if handler is None:
            logger.info('Unknown save path: %s', path)
            return


def main():
    parser = argparse.ArgumentParser(description='Proxy server.')
    parser.add_argument('-p', '--port', default=8080, type=int,
                        help='Port to listen on')
    parser.add_argument('-a', '--address', default='', type=str,
                        help='Address to listen on')
    parser.add_argument('-s', '--server', type=str,
                        default='',
                        help='InfluxDB Server DSN')
    parser.add_argument('--api_key', type=str,
                        help='Weather Underground API Key')
    parser.add_argument('--location', type=str,
                        help='Weather Underground location query.')
    log_choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    parser.add_argument('-l', '--log', dest='logLevel', default='INFO',
                        choices=log_choices, help='Set the logging level')
    args = parser.parse_args()
    # Set up clean logging to stderr
    log_level = getattr(logging, args.logLevel)
    datefmt = '%m/%d/%Y %H:%M:%S'
    log_format = '%(asctime)s'
    if (args.logLevel == 'DEBUG'):
        log_format = '{} %(filename)s'.format(log_format)
        log_format = '{} %(funcName)s:%(lineno)d'.format(log_format)
    log_format = '{} %(levelname)s: %(message)s'.format(log_format)
    logging.basicConfig(level=log_level, format=log_format, datefmt=datefmt)

    global influxdb
    if args.server != '':
        influxdb = args.server

    global api_key
    if args.api_key:
        api_key = args.api_key

    global location_query
    if args.location:
        location_query = args.location

    server_address = (args.address, args.port)
    HandlerClass = CarrierProxyRequestHandler
    ServerClass = proxy.ThreadingHTTPServer
    protocol = 'HTTP/1.1'

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    logging.info('Serving HTTP Proxy on %s port %s ...', sa[0], sa[1])
    httpd.serve_forever()
    return

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        exit(1)
