import pickle
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

        # XXX: Also for range?
        for field in form.get('facet.field'):
            if not args.has_key(field):
                # XXX: Ugh. Solr ignores fields that are [] or None, so we need
                # to give some value that we know will not return hits
                args[field] = 'slc.facetedcalendar.dummy'

        return args


    def _updateCriteriaArgs(self, args):
        request = self.request
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        # FIXME
        try:
            start_date = DateTime(int(request.get('start')))
            end_date = DateTime(int(request.get('end')))
            args['start'] = {'query': end_date, 'range':'max'}
            args['end'] = {'query': start_date, 'range':'min'}
        except TypeError:
            pass
        
        if getattr(self.calendar, 'overrideStateForAdmin', True) and \
                args.has_key('review_state'):
            # Solgema.fullcalendare removes the 'review_state' form the query,
            # we instead want it to have all the possible values, so that they
            # appear checked in the facet parameters box.
            pm = getToolByName(context,'portal_membership')
            member = pm.getAuthenticatedMember()
            if member and member.has_permission(ModifyPortalContent, context):
                args['review_state'] = catalog.uniqueValuesFor('review_state')
                
        facet_dict = {
                'facet.field': [],
                'facet.range': [],
                }
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
        args.update(facet_dict)
        return args


    def _updateRequest(self, args):
        """ Put the query pars on the request so that the facet parameters box
            knows about them.
        """
        if not hasattr(self.request, 'form'):
            self.request.set('form', {})

        for key, value in args.items():
            self.request[key] = value
            self.request.form[key] = value


    def _getArgsAndFilters(self, clear_form=False):
        context = aq_inner(self.context)
        sdm = getToolByName(context, 'session_data_manager')
        session = sdm.getSessionData()
        path = '/'.join(context.getPhysicalPath())
        form = session.get(path, {}) 

        if form.get('form_submitted', None):
            # XXX: This is ugly :(
            if clear_form:
                del form['form_submitted']
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
        args['use_solr'] = True
        args['facet']= 'true'
        brains = self._getBrains(args, filters)
        topicEventsDict = getMultiAdapter(
                                (context, self.request),
                                interfaces.ISolgemaFullcalendarTopicEventDict)
        return topicEventsDict.createDict(brains, args)


    def getFacetedEvents(self):
        context = aq_inner(self.context)
        args, filters = self._getArgsAndFilters(clear_form=True)
        args['use_solr'] = True
        args['facet']= 'true'
        self._updateRequest(args)
        return self._getBrains(args, filters)


