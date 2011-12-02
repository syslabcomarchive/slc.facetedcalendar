from zope.annotation.interfaces import IAnnotations
from z3c.form import button
from z3c.form import field
from z3c.form import form
from Products.Archetypes.utils import addStatusMessage
from slc.facetedcalendar import MessageFactory as _
from interfaces import IFacetsConfigForm

class FacetsConfigForm(form.Form):
    label = _(u"Facet Configuration Settings")
    ignoreContext = True
    fields = field.Fields(IFacetsConfigForm).select('facets',)
    buttons = button.Buttons(IFacetsConfigForm)

    def updateWidgets(self):
        """ Make sure that the form is aware of the already stored values.
        """
        form.Form.updateWidgets(self)
        widget_value = self.request.get('form.widgets.facets:list')
        if not widget_value:
            annotations = IAnnotations(self.context)
            widget_value = annotations.get('slc.facetedcalendar.facets', set())
        self.widgets['facets'].value = widget_value

    @button.handler(IFacetsConfigForm['save_facetedcalendar_config'])
    def save(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = '\n'.join([error.error.__str__() for error in errors])
            return 

        annotations = IAnnotations(self.context)
        annotations['slc.facetedcalendar.facets'] = data['facets']
        addStatusMessage(self.request, _('Filters Saved'), type='info')
        self.request.response.redirect('/'.join(self.context.getPhysicalPath()))

    @button.handler(IFacetsConfigForm['cancel_facetedcalendar_config'])
    def cancel(self, action):
        self.request.response.redirect('/'.join(self.context.getPhysicalPath()))

