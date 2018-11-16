$(document).ready(function () {
    $('#options-is_existing').on('change', function () {
        var option_selected = $('#options-is_existing').find(":selected").text();
        if (option_selected === "New files") {
            $("#newfiles").show();
            $("#existingfiles").hide();
            $("#generate_dataset").hide();
            $('#submit-button').prop('disabled', false);
        } else if (option_selected === "Existing files") {
            $("#newfiles").hide();
            $("#generate_dataset").hide();
            $("#existingfiles").show();
            $('#submit-button').prop('disabled', false);

        } else if (option_selected === "Generate data") {
            $("#newfiles").hide();
            $("#existingfiles").hide();
            $("#generate_dataset").show();
            $('#submit-button').prop('disabled', true);
        }
    });
    $("#existingfiles").hide();
    $("#generate_dataset").hide();
    $('#submit-button').prop('disabled', false);
    //
    // $('#is_existing').change(function () {
    //     if (this.checked) {
    //
    //         $("#newfiles").hide();
    //         $("#existingfiles").show();
    //     }
    //     else {
    //         // $("#existingfiles").find(":input").prop("disabled", true);
    //         // $("#newfiles").find(":input").prop("disabled", false);
    //         $("#newfiles").show();
    //         $("#existingfiles").hide();
    //     }
    // });
    // $("#existingfiles").find(":input").prop("disabled", true);
});

