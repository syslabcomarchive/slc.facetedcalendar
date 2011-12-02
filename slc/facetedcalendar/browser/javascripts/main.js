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
                $('#facetedcalendar-parameters').html(html);
            }
        });
    });
});
            
