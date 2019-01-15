$(document).ready(function(){
	   $(window).bind('scroll', function() {
	   var navHeight = $( window ).height() / 3 - 70;
			 if ($(window).scrollTop() > navHeight) {
				 $('.navbar').addClass('navbar-fixed-top');
			 }
			 else {
				 $('.navbar').removeClass('navbar-fixed-top');
			 }
		});
	});