var playing = true;

function token_session(token) {
    if (window.sessionStorage.getItem('token') == null) {
        window.sessionStorage.setItem('token', token);
    } else {
        if (token !== window.sessionStorage.getItem('token')) {
            window.sessionStorage.removeItem('token');
            window.location.href = "/login";
        }
    }
}

function activate_toggler(data) {
    $('#no-active-run').addClass('hide-element');
    $('#active-run').removeClass('hide-element');
    $('.theme-helper .theme-helper-toggler i ').css('animation-play-state', 'running');

    if (data.epochs != null) {
        let str = data.epochs.toString().padStart(6, "0");
        let txt = str.slice(0, 3) + ',' + str.slice(3);
        $("#iter-number-toggler").text(txt);
    }

    $("#model-toggler").text(data.model_name);

}

function deactivate_toggler() {
    $('#no-active-run').removeClass('hide-element');
    $('#active-run').addClass('hide-element');
    $('.theme-helper .theme-helper-toggler i ').css('animation-play-state', 'paused');
}
