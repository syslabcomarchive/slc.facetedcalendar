from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Solgema.fullcalendar import interfaces
from Solgema.fullcalendar.browser.views import SolgemaFullcalendarView
from Solgema.fullcalendar.browser.actions import BaseActionView 
                                                    
class FacetedCalendarView(SolgemaFullcalendarView):
    """ """

    def queryCatalog(self):
        context = aq_inner(self.context)
        source = getMultiAdapter(
                        (self.context, self.request),
                        interfaces.IEventSource)
        return source.getFacetedEvents()


class PropertiesGuard(BaseActionView):

    def __call__(self):
        selected_layout = getattr(self.context, 'layout', '')
        return selected_layout == 'facetedcalendar'
