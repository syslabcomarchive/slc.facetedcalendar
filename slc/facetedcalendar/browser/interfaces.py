from zope import schema
from zope.interface import Interface
from z3c.form import button
from slc.facetedcalendar import MessageFactory as _

class IAjaxView(Interface):
    """ """

    def render_faceted_parameters(self, start, end):
        """ """

class IFacetsConfigForm(Interface):
    """ """
    facets = schema.Set(
                title=_(u"Filter Parameters"),
                description=_(u"Choose which parameters a user can use to "
                    u"filter the calendar results."),
                value_type=schema.Choice(
                    vocabulary="slc.facetedcalendar.vocabularies.facetedcalendarparameters"
                ),
            )
    save_facetedcalendar_config = button.Button(title=_(u"Save"))
    cancel_facetedcalendar_config = button.Button(title=_(u"Cancel"))


class IFacetsConfigView(Interface):
    """ """
