$(document).ready(function() {
    $('#facetedcalendar-parameters').bind('fullcalendar-rendered', function(e, data) {
        var dates = data.data;
        $.ajax({
            url: '@@render_faceted_parameters_box',
            cache: false,
            data: {start: dates['start:int'], end: dates['end:int'] },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(textStatus);
                console.log(errorThrown);
            },
            success: function(html) {
                $('#facetedcalendar-parameters').html(html);
            }
        });
    });
    $("a#facetedcalendar-config").live('click', function(e) {
        e.preventDefault();
        $.ajax({
            url: '@@render_faceted_parameters_config',
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(textStatus);
                console.log(errorThrown);
            },
            success: function(html) {
                $('div#portal-facetsquery').hide('fast', function() {
                    $('div#portal-facetsconfig').hide().append(html).fadeIn('fast');
                });
            }
        });
    });
    $("input#form-buttons-cancel_facetedcalendar_config").live('click', function(e) {
        e.preventDefault();
        $('div#portal-facetsconfig-form').hide('fast', function() {
            $('div#portal-facetsquery').show('fast');
        }).remove();
    });

    $('#browsing-menu input[type=checkbox]').live('click', function () { 
        var query_string = $("form#browsing-menu").serialize();
        $.ajax({
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
    });
});
            
