function define_steps(page, tam) {
    var element = document.getElementById(page);
    element.className.replace("btn btn-default", "btn btn-primary");
    for (var i = page + 2; i < tam; i++) {
        var nelement = document.getElementById(i);
        nelement.classList.add('disabled');
        nelement.disabled = true;
    }
    element.className = element.className.replace("btn btn-default", "btn btn-primary");
    if (page > 0) {
        for (var i = page + 1; i < tam; i++) {
            var nelement = document.getElementById(i);
            nelement.classList.add('disabled');
            nelement.disabled = true;
        }
    }

}

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
//
// $(document).ready(function () {
//
//     $('#sidebarCollapse').on('click', function () {
//         $('#sidebar').toggleClass('active');
//     });
//
// });