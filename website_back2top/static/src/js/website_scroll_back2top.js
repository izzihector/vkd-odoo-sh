$(document).ready(function()
{
    $('body').prepend('<a href="#" class="back-to-top">Back to Top</a>');
    var amountScrolled = 300;

    $(window).scroll(function() {
        if ($(window).scrollTop() > amountScrolled) {
            $('a.back-to-top').fadeIn('slow');
        } else {
            $('a.back-to-top').fadeOut('slow');
        }
    });

    $('a.back-to-top').on('click', function()
    {
        $('body,html').animate({
            scrollTop: 0
        }, 500);
        return false;
    });
});
