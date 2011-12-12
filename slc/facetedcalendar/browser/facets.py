from copy import deepcopy
from logging import getLogger

from DateTime import DateTime
from ZTUtils import make_hidden_input

from Products.Archetypes.interfaces import IVocabulary
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex

from collective.solr.browser import facets 

log = getLogger(__name__)

class SearchFacetsView(BrowserView, facets.FacetMixin):
    """ view for displaying facetting info as provided by solr searches """

    def __init__(self, context, request):
        self.facet_fields, dependencies = facets.facetParameters(context, request)

        self.default_query = {'facet': 'true',
                              'facet.field': self.facet_fields }

        self.submenus = [dict(title=field, id=field) for field in self.facet_fields]
        self.queryparam = 'fq'
        BrowserView.__init__(self, context, request)


    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw
        self.form = deepcopy(self.default_query)
        self.form.update(deepcopy(self.request.form))
        catalog = getToolByName(self.context, 'portal_catalog')

        if not 'results' in self.kw or \
                    not hasattr(self.kw['results'], 'facet_counts'):

            query = deepcopy(self.form)
            self.results = catalog(query)
            if not 'results' in self.kw:
                self.kw['results'] = self.results

        if not getattr(self, 'results', None):
            self.results = self.kw['results']

        facet_counts = getattr(self.results, 'facet_counts', {})
        voctool = getToolByName(self.context, 'portal_vocabularies', None)
        self.vocDict = dict()

        index_dict = catalog._catalog.indexes
        for field in self.facet_fields:
            voc = voctool.getVocabularyByName(field)
            if IVocabulary.providedBy(voc):
                self.vocDict[field] = ( voc.Title(), 
                                        voc.getVocabularyDict(self.context))
            else:
                content = dict()
                if not isinstance(index_dict[field], ZCTextIndex):
                    field_values = catalog.uniqueValuesFor(field)

                    if isinstance(index_dict[field], DateIndex):
                        for value in field_values:
                            content[value] = (DateTime(value).strftime('%d.%m.%Y'), None)
                    else:
                        for value in field_values:
                            content[value] = (value, None)

                self.vocDict[field] = (self.getFieldFriendlyName(field), content)

        return super(SearchFacetsView, self).__call__(*args, **kw)


    def getFieldFriendlyName(self, field):
        atct = getToolByName(self.context, 'portal_atct')
        return atct.getIndex(field).friendlyName


    def getCounts(self):
        res = self.results or self.kw['results']
        if not hasattr(res, 'facet_counts'):
            return {}
        counts = res.facet_counts['facet_fields']
        for rng in res.facet_counts['facet_ranges']:
            counts[rng] = res.facet_counts['facet_ranges'][rng]['counts']
        return counts


    def sort(self, submenu):
        return sorted(submenu, key=lambda x:x['count'], reverse=True)


    def getMenu(self, 
                id='ROOT', 
                title=None, 
                vocab={}, 
                counts=None, 
                parent=None, ):
        menu = []
        if not vocab and id == 'ROOT':
            vocab = self.vocDict
        if not counts and id == 'ROOT':
            counts = self.getCounts()

        count = 0
        if isinstance(counts, int):
            count = int(counts)

        if vocab:
            for term in vocab:
                submenu = []
                counts_sub = None
                if isinstance(counts, dict):
                    counts_sub = counts.get(term, None)
                title_sub = ''
                vocab_sub = vocab.get(term, {})
                if vocab_sub:
                    title_sub = vocab_sub[0]
                    vocab_sub = vocab_sub[1]
                submenu = self.getMenu(
                                    id=term, 
                                    title=title_sub, 
                                    vocab=vocab_sub, 
                                    counts=counts_sub, 
                                    parent=id, )
                menu.append(submenu)
            menu = self.sort(menu)

        selected = False
        if parent not in [None, 'ROOT']:
            form = getattr(self.request, 'form', {})
            queried = form.get(parent)
            if queried == id or \
                    isinstance(queried, (list, tuple)) and id in queried:
                selected = True

        return dict(id=id, 
                    title=title, 
                    selected=selected, 
                    count=count, 
                    content=menu)


    def showSubmenu(self, submenu):
        """Returns True if submenu has an entry with query or clearquery set,
            i.e. should be displayed
        """
        return not filter(lambda x: x.get('selected', False) \
                          or x['count']>0, submenu) == []


    def expandSubmenu(self, submenu):
        """Returns True if submenu has an entry with clearquery set, i.e.
           should be displayed expanded
        """
        return not filter(lambda x: x.has_key('clearquery'), submenu) == []


    def getHiddenFields(self):
        return make_hidden_input([x for x in self.form.items() if x[0] not in self.facet_fields])

