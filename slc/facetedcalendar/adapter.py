import pickle
from zope.component import queryAdapter

from Products.CMFCore.utils import getToolByName

from collective.solr.flare import PloneFlare

from Solgema.fullcalendar.browser import adapters
from Solgema.fullcalendar import interfaces
from Solgema.fullcalendar.browser.solgemafullcalendar_views import getColorIndex

try:
    from plone.event.interfaces import IRecurrenceSupport
    HAS_RECCURENCE_SUPPORT = True
except ImportError:
    HAS_RECCURENCE_SUPPORT = False

class CatalogSearch(adapters.SolgemaFullcalendarCatalogSearch):

    def searchResults(self, args):
        """ Force solr use.

            Also, store and retrieve args from a pickle, since solr 
            returns them with dates removed.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        # XXX: This is temporary until the bug in solr is fixed.
        qdict = pickle.loads(pickle.dumps(args))
        qdict['use_solr'] = True
        results = catalog.searchResults(qdict)
        return results
                            
class TopicEventDict(adapters.SolgemaFullcalendarTopicEventDict):

    def dictFromFlare(self, flare, args):
        eventsFilter = queryAdapter(self.context,
                                    interfaces.ISolgemaFullcalendarEditableFilter)
        editpaths = eventsFilter.filterEvents(args)

        memberid = self.context.portal_membership.getAuthenticatedMember().id
        editable = (memberid == flare.Creator or flare.getURL() in editpaths)

        if getattr(flare, 'SFAllDay', None) in [False, True]:
            allday = flare.SFAllDay
        else:
            allday = (flare.end - flare.start > 1.0)

        copycut = ''
        if self.copyDict and flare.getPath() == self.copyDict['url']:
            copycut = self.copyDict['op'] == 1 and ' event_cutted' or ' event_copied'

        typeClass = ' type-'+flare.portal_type
        colorIndex = getColorIndex(self.context, self.request, brain=flare)
        extraClass = self.getExtraClass(flare)
        if HAS_RECCURENCE_SUPPORT:
            occurences = IRecurrenceSupport(flare.getObject()).occurences()
        else:
            occurences = [(flare.start.rfc822(), flare.end.rfc822())]

        events = []
        for occurence_start, occurence_end in occurences:
            events.append({
                "id": "UID_%s" % (flare.UID),
                "title": flare.Title,
                "description": flare.Description,
                "start": HAS_RECCURENCE_SUPPORT and occurence_start.isoformat() or occurence_start,
                "end": HAS_RECCURENCE_SUPPORT and occurence_end.isoformat() or occurence_end,
                "url": flare.getURL(),
                "editable": editable,
                "allDay": allday,
                "className": "contextualContentMenuEnabled state-" + \
                                str(flare.review_state) + \
                                (editable and " editable" or "") + \
                                copycut + typeClass+colorIndex+extraClass})
        return events


    def createDict(self, items=[], args={}):
        li = []
        for item in items:
            if type(item) == PloneFlare:
                li.extend(self.dictFromFlare(item, args))
            elif hasattr(item, '_unrestrictedGetObject'):
                li.extend(self.dictFromBrain(item, args))
            else:
                li.extend(self.dictFromObject(item))
        return li

