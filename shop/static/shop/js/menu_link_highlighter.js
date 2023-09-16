   var currentPageUrl = window.location.href;
    var menuLinks = document.querySelectorAll('.container-fluid ul li a');
    menuLinks.forEach(function(link) {
        if (link.href === currentPageUrl) {
            link.parentElement.classList.add('active');
        }
    });

    var dropdownLinks = document.querySelectorAll('.container-fluid ul li.dropdown ul li a');
    dropdownLinks.forEach(function(link) {
        if (link.href === currentPageUrl) {
            link.parentElement.classList.add('active');
            var parentDropdown = link.closest('.dropdown');
            if (parentDropdown) {
                parentDropdown.classList.add('active');
            }
        }
    });