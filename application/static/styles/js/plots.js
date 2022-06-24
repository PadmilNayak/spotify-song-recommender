$('#first_cat').on('change',function(){

    $.ajax({
        url: "/bar",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('first_cat').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data );
        }
    });
})

$('#first_cat_2').on('change',function(){

    $.ajax({
        url: "/bar2",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('first_cat_2').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph2', data );
        }
    });
})

$('#first_cat_3').on('change',function(){

    $.ajax({
        url: "/line",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('first_cat_3').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('linegraph', data );
        }
    });
})