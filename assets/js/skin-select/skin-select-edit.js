
$(document).ready(function() { 
	
	// toggle skin select	
	$("#skin-select #toggle").click(function() { 
	//$('.wrap-fluid').fadeOut(500);
		if($(this).hasClass('active')) {
			$(this).removeClass('active')

			$('#skin-select').animate({ left:0 }, 100);		
			$('.wrap-fluid').css({"float":"right", "width":"100%"	});
			$('#skin-select li').css({"text-align":"left"});
			$('#skin-select li span, ul.topnav h4').css({"display":"inline-block", "float":"none"});
			$('body').css({"padding-left":"250px"});	
			$('.ul.topnav h4').css({"display":"none"});
			$('.tooltip-tip2').tooltipster('disable');
			$('.tooltip-tip').tooltipster('disable');
			$('.datepicker-wrap').css({"position":"absolute", "right":"300px"});
		
		

			
		} else {
			$(this).addClass('active')

			//$('#skin-select').animate({ left:-200 }, 100);
			$('#skin-select').css({"left":"-200px"});

			$('.wrap-fluid').css({"float":"right", "width":"100%"});
			$('#skin-select li').css({"text-align":"right"});
			$('#skin-select li span, ul.topnav h4').css({"display":"none"});
			$('body').css({"padding-left":"40px"});
			$('.tooltip-tip2').tooltipster('enable');
			$('.tooltip-tip').tooltipster('enable');
			$('.datepicker-wrap').css({"position":"absolute", "right":"84px"});




	

		}if ($(window).width() <= 767) {


        	$('#skin-select').css({"left":"-200px"});

			$('.wrap-fluid').css({"float":"right", "width":"100%"});
			$('#skin-select li').css({"text-align":"right"});
			$('#skin-select li span, ul.topnav h4').css({"display":"none"});
			$('body').css({"padding-left":"40px"});
			$('.tooltip-tip2').tooltipster('enable');
			$('.tooltip-tip').tooltipster('enable');
			$('.datepicker-wrap').css({"position":"absolute", "right":"84px"});
       
            $('.tooltip-tip2').tooltipster('enable');
            $('.tooltip-tip').tooltipster('enable');
          


        }

		return false;
	});
	
	
	// show skin select for a second
	setTimeout(function(){ $("#skin-select #toggle").addClass('active').trigger('click'); },10)

	//$(window).resize(function() {

        

   // });
	
	
}); // end doc.ready

