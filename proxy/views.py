# import datetime
import logging

# from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from requests import Request, Session

# from defusedxml import ElementTree as ET

# Get an instance of a logger
logger = logging.getLogger(__name__)


def proxy_request(request):
    headers = dict(request.headers)
    full_uri = request.build_absolute_uri()
    method = request.method
    content_length = int(request.headers.get("Content-Length", 0) or 0)
    #    now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    #    if settings.get("SAVE_REQUESTS", False) and content_length > 0 and request.method == "POST":
    #        fname = "req_{uri}_{now}.xml".format(
    #            uri=request.resolver_match.func.__name__, now=now
    #        )
    #        req_file = "{media}/{fname}".format(media=settings.MEDIA_ROOT, fname=fname)
    #        with open(req_file, "w") as f:
    #            f.write(request.POST["data"])
    logger.debug("{method}: {uri}".format(method=method, uri=full_uri))
    headers["Content-Length"] = str(content_length)
    s = Session()
    req = Request(method, full_uri, headers=headers, data=request.body)
    prepped = req.prepare()
    r = s.send(prepped)
    logger.debug("Response: {response}".format(response=r.content))
    #    if settings.get("SAVE_RESPONSES", False) and r.content:
    #        fname = "resp_{uri}_{now}.xml".format(
    #            uri=request.resolver_match.func.__name__, now=now
    #        )
    #        req_file = "{media}/{fname}".format(media=settings.MEDIA_ROOT, fname=fname)
    #        with open(req_file, "wb") as f:
    #            f.write(r.content)
    return r


# Create your views here.
@csrf_exempt
def release_notes(request, uri=None):
    """Handle release note requests.

    Release note requests come in with a different URI as the path so they
    must be handled differently.
    """
    logger.info("Received release_notes request")
    headers = dict(request.headers)
    full_uri = "http{uri}".format(uri=uri)
    method = request.method
    content_length = int(request.headers.get("Content-Length", 0) or 0)
    logger.debug("{method}: {uri}".format(method=method, uri=full_uri))
    headers["Content-Length"] = str(content_length)
    s = Session()
    req = Request(method, full_uri, headers=headers, data=request.body)
    prepped = req.prepare()
    r = s.send(prepped)
    logger.debug("Response: {response}".format(response=r.content))
    return r


@csrf_exempt
def default_handler(request, path=None):
    """Handle all other requests

    This view handles all other request types
    """
    logger.info("Unmanaged path: {path}".format(path=path))
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def alive(request):
    """Handle alive checks.

    This view handles proxying alive checks performed by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_overview(request, serial):
    """Handle system posts.

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_profile(request, serial):
    """Handle system profile posts.

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_status(request, serial):
    """Handle system status posts.

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_dealer(request, serial):
    """Handle system dealer posts.

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_notifications(request, serial):
    """Handle system notifications posts.

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_idu_config(request, serial):
    """Handle system In-Door Unit posts.

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_odu_config(request, serial):
    """Handle system Out-Door Unit posts.

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response


@csrf_exempt
def systems_equipment_events(request, serial):
    """Handle system equipment events posts

    This view handles processing system status updates by the HVAC unit.
    """
    r = proxy_request(request)
    response = HttpResponse(
        content=r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type"),
    )
    return response
