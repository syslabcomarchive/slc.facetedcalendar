from zope.publisher.interfaces.browser import IBrowserRequest
from Solgema.fullcalendar.interfaces import ISolgemaFullcalendarMarker

class IProductLayer(IBrowserRequest):
    """ Marker interface for requests indicating the staralliance.theme
        package has been installed.
    """

class IFacetedCalendarMarker(ISolgemaFullcalendarMarker):
    """ A marker for items that can be displayed as faceted calendar
    """
