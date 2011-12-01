import pickle
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATContentTypes.interfaces.topic import IATTopic
from collective.solr.interfaces import IFlare
from Solgema.fullcalendar.browser import adapters
from Solgema.fullcalendar import interfaces
from slc.facetedcalendar.interfaces import IProductLayer

class CatalogSearch(adapters.SolgemaFullcalendarCatalogSearch):

    def searchResults(self, args):
        """ Force solr use.

            Also, store and retrieve args from a pickle, since solr's mangling
            returns them with dates removed.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        # XXX: This is temporary until the bug in solr is fixed.
        # Try: from copy import deepcopy
        qdict = pickle.loads(pickle.dumps(args))
        qdict['use_solr'] = True
        results = catalog.searchResults(qdict)
        return results
                            

class ColorIndexGetter(adapters.ColorIndexGetter):
    """ Reuses Solgema.fullcalendar's ColorIndexGetter but adapt's
        collective.solr's IFlare type instead of ICatalogBrain.
    """
    adapts(Interface, Interface, IFlare)


class TopicEventSource(adapters.TopicEventSource):
    """ """
    implements(interfaces.IEventSource)
    adapts(IATTopic, IProductLayer)

    def getFacetedEvents(self):
        context = aq_inner(self.context)
        request = self.request
        response = request.response

        args, filters = self._getCriteriaArgs()
        start_date = DateTime(int(request.get('start')))
        end_date = DateTime(int(request.get('end')))
        args['start'] = {'query': end_date, 'range':'max'}
        args['end'] = {'query': start_date, 'range':'min'}

        facet_dict = {
                'use_solr': True,
                'facet': 'true',
                'facet.field': [],
                'facet.range': [],
                }
        catalog = getToolByName(self.context, 'portal_catalog')
        for index in args.keys():
            if index in catalog.indexes():
                if type(args[index]) == dict and 'range' in args[index].keys():
                    facet_dict['facet.range'].append(index)
                else:
                    facet_dict['facet.field'].append(index)

        # XXX: This still feels very fragile... what about other range queries
        # that are not dates?
        facet_dict['facet.range.start'] = 'NOW/DAY-6MONTHS'
        facet_dict['facet.range.end'] = 'NOW/DAY+6MONTHS'
        facet_dict['facet.range.gap'] = '+7DAYS'

        if getattr(self.calendar, 'overrideStateForAdmin', True) and \
                args.has_key('review_state'):
            # Solgema.fullcalendare removes the 'review_state' form the query,
            # we instead want it to have all the possible values, so that they
            # appear checked in the facet parameters box.
            pm = getToolByName(context,'portal_membership')
            member = pm.getAuthenticatedMember()
            if member and member.has_permission(ModifyPortalContent, context):
                args['review_state'] = catalog.uniqueValuesFor('review_state')

        # Put the query pars on the request so that the facet parameters box
        # knows about them
        args.update(facet_dict)
        for key, value in args.items():
            request.set(key, value)

        return self._getBrains(args, filters)

