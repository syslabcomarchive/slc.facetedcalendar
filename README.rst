Introduction
============

slc.facetedcalendar provides faceted search inside a calendar.

It makes use of `collective.solr`_ for the faceted search and
`Solgema.fullcalendar`_ for the calendar view.

.. _collective.solr: https://github.com/Jarn/collective.solr
.. _Solgema.fullcalendar: https://github.com/Solgema/Solgema.fullcalendar


Usage
=====

Make sure that collective.solr is configured for faceted search by going to
Plone/@@solr-controlpanel. Refer to the collective.solr docs for more info.

On any Topic, for example in the Events folder, you can now enable the 'Faceted
Calendar' view by clicking on 'Display' and choosing it from the dropdown.

You should see the Solgema.fullcalendar calendar together with a query box on the
right that lets you select the different facet parameters.

The events in the calendar should automatically update every time you choose
another facet.

You can choose which facet parameters to be shown by clicking the "Edit" link
on the query box.


