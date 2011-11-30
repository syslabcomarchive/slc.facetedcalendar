from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interfaces import IAjaxView

class AjaxView(BrowserView):
    implements(IAjaxView)
    template = ViewPageTemplateFile('templates/faceted_parameters_box.pt')

    def render_faceted_parameters_box(self, start, end):
        """ """ 
        return self.template()
