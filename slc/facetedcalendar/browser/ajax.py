from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from slc.facetedcalendar import utils
from interfaces import IAjaxView

class AjaxView(BrowserView):
    implements(IAjaxView)
    template = ViewPageTemplateFile('templates/faceted_parameters_box.pt')

    def render_faceted_parameters_box(self, start, end):
        """ """ 
        context = aq_inner(self.context)
        view = getMultiAdapter((context, self.request), name='facetedcalendar')
        return self.template(results=view.get_results())

    def render_faceted_parameters_config(self):
        """ """ 
        context = aq_inner(self.context)
        view = getMultiAdapter((context, self.request), name='facetedcalendar_embeddedconfig')
        return view()

    def save_form_in_session(self, **kw):
        """ """
        utils.save_form_in_session(self.context, self.request)
        
