$(document).ready(function () {
    $('#training_advanced_title').hide();


    gui_editor_change();


    $('#custom_model-' +
        'gui_editor').bind('change', function () {
        gui_editor_change();
    })
});

function gui_editor_change() {
    if ($('#custom_model-gui_editor').val() === 'True') {
        $('#network').hide();
        $('#training_advanced').hide();
    } else {
        $('#network').show();
        $('#training_advanced').show();
    }
}