function updateCalendar() {
    var query_string = jq("form#browsing-menu").serialize();
    jq.ajax({
        url: '@@save_form_in_session?'+query_string,
        cache: false,
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(textStatus);
            console.log(errorThrown);
        },
        success: function(html) {
            var calendar = jq('#calendar').fullCalendar('refetchEvents');
        }
    });
}

jq(document).ready(function() {
    jq('#facetedcalendar-parameters').bind('fullcalendarRendered', function(e, data) {
        jq.ajax({
            url: '@@render_faceted_parameters_box',
            cache: false,
            data: {start: data.start.valueOf()/1000, end: data.end.valueOf()/1000 },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(textStatus);
                console.log(errorThrown);
            },
            success: function(html) {
                jq('#facetedcalendar-parameters').html(html);
            }
        });
    });
    jq("a#facetedcalendar-config").live('click', function(e) {
        e.preventDefault();
        jq.ajax({
            url: '@@render_faceted_parameters_config',
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(textStatus);
                console.log(errorThrown);
            },
            success: function(html) {
                jq('div#portal-facetsquery').hide('fast', function() {
                    jq('div#portal-facetsconfig').hide().append(html).fadeIn('fast');
                });
            }
        });
    });
    jq("input#form-buttons-cancel_facetedcalendar_config").live('click', function(e) {
        e.preventDefault();
        jq('div#portal-facetsconfig-form').hide('fast', function() {
            jq('div#portal-facetsquery').show('fast');
        }).remove();
    });
    jq('#browsing-menu input[type=checkbox]').live('click', function () { 
        updateCalendar();
    });
    jq("form#browsing-menu").live('submit', function (e) {
        e.preventDefault();
        updateCalendar();
    });
});
            
