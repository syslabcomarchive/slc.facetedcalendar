from zope.component import getMultiAdapter
from Acquisition import aq_inner
from persistent.dict import PersistentDict
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Solgema.fullcalendar import interfaces
from Solgema.fullcalendar.browser.views import SolgemaFullcalendarView
from Solgema.fullcalendar.browser.actions import BaseActionView 
                                                    
class FacetedCalendarView(SolgemaFullcalendarView):
    """ """

    def get_results(self):
        """ """
        context = aq_inner(self.context)
        source = getMultiAdapter(
                        (self.context, self.request),
                        interfaces.IEventSource)
        return source.getFacetedEvents()


class UserQuerySubmitted(BrowserView):
    
    def __call__(self):
        """ """
        sdm = getToolByName(self.context, 'session_data_manager')
        session = sdm.getSessionData(create=True)
        path = '/'.join(self.context.getPhysicalPath())
        pdict = PersistentDict()
        pdict.update(self.request.form)
        session.set(path, pdict) 
        return self.request.RESPONSE.redirect(path)


class PropertiesGuard(BaseActionView):

    def __call__(self):
        selected_layout = getattr(self.context, 'layout', '')
        return selected_layout in [ 'facetedcalendar',
                                    'solgemafullcalendar_view']
