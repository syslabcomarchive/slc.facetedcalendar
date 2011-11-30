$(document).ready(function() {
    $('#facetedcalendar-parameters').bind('fullcalendar-rendered', function(e, data) {
        var data = data.data;
        $.ajax({
            url: '@@render_faceted_parameters_box',
            cache: false,
            data: {start: data['start:int'], end: data['end:int'] },
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
            
