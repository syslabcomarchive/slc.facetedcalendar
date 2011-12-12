import pickle
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from DateTime import DateTime

from Products.ATContentTypes.interfaces.topic import IATTopic
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex

from collective.solr.interfaces import IFlare
from Solgema.fullcalendar.browser import adapters
from Solgema.fullcalendar import interfaces

from collective.solr.browser.facets import facetParameters

from slc.facetedsearch.interfaces import IDefaultRangesGetter
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

    def _getFormArgs(self, form):
        catalog = getToolByName(self.context, 'portal_catalog')
        args = {}
        for key, value in form.items():
            try:
                index = catalog._catalog.getIndex(key)
            except KeyError:
                if key != '_':
                    args[key] = value
            else:
                if isinstance(index, DateIndex):
                    # Date values need to be converted...
                    range = value.get('range') 
                    query = value.get('query')
                    if range in ['min','max']:
                        query = DateTime(query)
                    elif range == 'min:max':
                        query = [DateTime(query[0]), DateTime(query[1])]
                    value = {'range':range, 'query': query}
                args[key] = value

        return args


    def _updateCriteriaArgs(self, args):
        request = self.request
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        start_date = DateTime(int(request.get('start')))
        end_date = DateTime(int(request.get('end')))
        args['start'] = {'query': end_date, 'range':'max'}
        args['end'] = {'query': start_date, 'range':'min'}
        
        if getattr(self.calendar, 'overrideStateForAdmin', True) and \
                args.has_key('review_state'):
            # Solgema.fullcalendare removes the 'review_state' form the query,
            # we instead want it to have all the possible values, so that they
            # appear checked in the facet parameters box.
            pm = getToolByName(context,'portal_membership')
            member = pm.getAuthenticatedMember()
            if member and member.has_permission(ModifyPortalContent, context):
                # args['review_state'] = catalog.uniqueValuesFor('review_state')
                del args['review_state']
        return args
                

    def _addFacetArgs(self, args):
        facet_dict = {'use_solr':True, 'facet':'true'}
        annotations = IAnnotations(self.context)
        facets = annotations.get('slc.facetedcalendar.facets', None)
        if facets is None:
            facets, dependencies = facetParameters(self.context, self.request)

        for facet in facets:
            facet_dict['facet.field'] = list(facets)

        args.update(facet_dict)
        return args


    def _updateRequest(self, args):
        """ Put the query pars on the request so that the facet parameters box
            knows about them.
        """
        if not hasattr(self.request, 'form'):
            self.request.set('form', {})

        for key, value in args.items():
            if isinstance(value, tuple):
                # Convert tuples to lists. ZUtils.make_hidden_input requires it
                value = list(value)
            self.request[key] = value
            self.request.form[key] = value


    def _getArgsAndFilters(self, faceting=False):
        context = aq_inner(self.context)
        sdm = getToolByName(context, 'session_data_manager')
        session = sdm.getSessionData()
        path = '/'.join(context.getPhysicalPath())
        form = session.get(path, {}) 
        if form.get('form.submitted', None):
            if faceting:
                # The query box (which requires faceting info) is called after
                # the events are queried for. So we can now remove the flag.
                del form['form.submitted']
            args = self._getFormArgs(form)
            filters = []
        else:
            args, filters = self._getCriteriaArgs()
            args = self._updateCriteriaArgs(args)
        return args, filters


    def getEvents(self):
        context = aq_inner(self.context)
        args, filters = self._getArgsAndFilters()
        self._updateRequest(args)
        brains = self._getBrains(args, filters)
        topicEventsDict = getMultiAdapter(
                                (context, self.request),
                                interfaces.ISolgemaFullcalendarTopicEventDict)
        return topicEventsDict.createDict(brains, args)


    def getFacetedEvents(self):
        context = aq_inner(self.context)
        args, filters = self._getArgsAndFilters(faceting=True)
        args = self._addFacetArgs(args)
        self._updateRequest(args)
        return self._getBrains(args, filters)


class DefaultRangesGetter(object):
    implements(IDefaultRangesGetter)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def getDefaultRanges(self):
        """ """
        return []

