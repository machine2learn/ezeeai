$('form').submit(function () {
    var train_split = r1;
    var val_split = r2;
    var test_split = r3;
    var input = $("<input>")
        .attr("type", "hidden")
        .attr("name", "train_split").val(train_split);
    $('form').append($(input));
    input = $("<input>")
        .attr("type", "hidden")
        .attr("name", "val_split").val(val_split);
    $('form').append($(input));
    input = $("<input>")
        .attr("type", "hidden")
        .attr("name", "test_split").val(test_split);
    $('form').append($(input));
    //#TODO VALIDATION
});

function prettify(num) {
    var n = num.toString();
    return n.replace(/(\d{1,3}(?=(?:\d\d\d)+(?!\d)))/g, "$1" + ",");
}

var $range1 = $(".js-range-slider-1"),
    $range2 = $(".js-range-slider-2"),
    $range3 = $(".js-range-slider-3"),
    $result = $(".js-result"),
    range_instance_1,
    range_instance_2,
    range_instance_3;

var max = 100;

var r1 = 70;
var r2 = 30;
var r3 = 0;

$range1.ionRangeSlider({
    type: "single",
    min: 0,
    max: 100,
    from: 70,
    grid: true,
    skin: 'modern',
    onStart: function (data) {
        $result.text(prettify(r1 + r2 + r3));
    },

    onFinish: function (data) {
        if (data.from < 50) {
            range_instance_1.update({
                from: 50
            });
        } else {
            if ((data.from + r2 + r3) > max) {
                range_instance_1.update({
                    from: max - r2 - r3
                });
            }
        }
        r1 = data.from;
        $result.text(prettify(r1 + r2 + r3));
        toggle_button();
    }
});
range_instance_1 = $range1.data("ionRangeSlider");

$range2.ionRangeSlider({
    type: "single",
    min: 0,
    max: 100,
    from: 30,
    grid: true,
    onStart: function (data) {
        $result.text(prettify(r1 + r2 + r3));
    },
    onFinish: function (data) {
        if (data.from <= 5) {
            range_instance_2.update({
                from: 5
            });
        } else {
            if ((data.from + r1 + r3) > max) {
                range_instance_2.update({
                    from: max - r1 - r3
                });
            }
        }
        r2 = data.from;
        $result.text(prettify(r1 + r2 + r3));
        toggle_button();
    }
});
range_instance_2 = $range2.data("ionRangeSlider");

$range3.ionRangeSlider({
    type: "single",
    min: 0,
    max: 100,
    from: 0,
    grid: true,
    onStart: function (data) {
        $result.text(prettify(r1 + r2 + r3));
    },
    onFinish: function (data) {
        if ((data.from + r1 + r2) > max) {
            range_instance_3.update({
                from: max - r1 - r2
            });
        }
        r3 = data.from;
        $result.text(prettify(r1 + r2 + r3));
        toggle_button();
    }
});
range_instance_3 = $range3.data("ionRangeSlider");

// function toggle_button(){
//     if ((r1 + r2 + r3) < max){
//         $("#submit").attr('disabled','disabled');
//     }else{
//         $("#submit").removeAttr('disabled');
//     }
//
// }

function toggle_button(){
    if ((r1 + r2 + r3) < max){
        $("#splitTabContinue").attr('disabled','disabled');
    }else{
        $("#splitTabContinue").removeAttr('disabled');
    }

}