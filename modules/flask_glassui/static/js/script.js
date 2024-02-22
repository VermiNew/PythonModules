window.onload = function () {
    var urlParams = new URLSearchParams(window.location.search);
    var animationDisabled = urlParams.get('animation') === 'disable';
    // ?animation=disabled

    var glassEffect = document.querySelector('.glass-effect');
    var content = document.querySelector('.content');
    var buttons = document.querySelector('.buttons');

    if (!animationDisabled) {
        glassEffect.style.display = 'block';
        glassEffect.style.transition = 'all 1s ease-in-out';
        content.style.transition = 'opacity 0.5s ease-in-out';
        buttons.style.transition = 'opacity 0.5s ease-in-out';
        setTimeout(function () {
            glassEffect.style.transform = 'scale(1)';
            glassEffect.style.opacity = 1;
            setTimeout(function () {
                content.style.opacity = 1;
                buttons.style.opacity = 1;
            }, 1000);
        });
    } else {
        glassEffect.style.display = 'block';
        glassEffect.style.transform = 'scale(1)';
        glassEffect.style.opacity = 1;
        content.style.opacity = 1;
        buttons.style.opacity = 1;
    }
};
