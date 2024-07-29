document.addEventListener('DOMContentLoaded', function () {
    var resizer = document.getElementById('resizer');
    var leftPanel = document.getElementById('fileList');
    var rightPanel = document.getElementById('contentArea');
    var isDragging = false, startX, startWidth;

    resizer.addEventListener('mousedown', function (e) {
        isDragging = true;
        startX = e.clientX;
        startWidth = leftPanel.offsetWidth;
        document.documentElement.addEventListener('mousemove', onDrag, false);
        document.documentElement.addEventListener('mouseup', onStopDrag, false);
    });

    function onDrag(e) {
        if (!isDragging) return;
        var newWidth = startWidth + e.clientX - startX;
        if (newWidth < 100) newWidth = 100;  // Minimum width for the sidebar
        if (newWidth > window.innerWidth - 200) newWidth = window.innerWidth - 200;  // Maximum width for the sidebar
        leftPanel.style.width = newWidth + 'px';
        rightPanel.style.flex = '1 1 auto';  // Make sure content area resizes correctly
    }

    function onStopDrag(e) {
        isDragging = false;
        document.documentElement.removeEventListener('mousemove', onDrag, false);
        document.documentElement.removeEventListener('mouseup', onStopDrag, false);
    }

    document.querySelectorAll('#fileList a').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            fetchContent(e.target.getAttribute('data-url'));
        });
    });

    function fetchContent(url) {
        fetch(url)
            .then(response => response.text())
            .then(text => {
                rightPanel.innerHTML = '<pre>' + text + '</pre>';
            });
    }
});
