$("document").ready(function() {
	var colors = new Array;

	// Disable all .switch stylesheets and build array of colours
	$(".switch[rel='stylesheet']").each(function() {
		$(this).attr("disabled", "true");
		colors.push($(this).css("color"));
	});
	
	
	$(colors).each(function(index, el) {
		$("#sheetswitch").append("<a class='swatch' style='background-color:" + el + ";'></a>");
	});
	
	$("#sheetswitch").append("<a href='#' class='sheetswitch_next'><img src='./images/1rightarrow.png' /></a>");
	
	$(".swatch").click(function() {
		$(".swatch").removeClass("swatch_hi");
		$(this).addClass("swatch_hi");
		var index = $(".swatch").index(this);
		$(".switch[rel='stylesheet']").attr("disabled", "true");
		$(".switch[rel='stylesheet']").eq(index).attr("disabled", "");
		$.cookie('mysite_sheetswitch_idx', index, {expires: 7});
	});
	
	$(".sheetswitch_next").click(function() {
		var selected = $(".switch[rel='stylesheet']").filter(function () { return $(this).attr("disabled") == false; });
		var current_idx = $(".switch[rel='stylesheet']").index($(selected));
		var length = $(".switch[rel='stylesheet']").size();
		
		if (current_idx >= 0) {
			var next = current_idx + 1;
			if (next > (length - 1)) next = 0;
			
			$(".switch[rel='stylesheet']").attr("disabled", "true");
			$(".switch[rel='stylesheet']").eq(next).attr("disabled", "");
			
			$(".swatch").removeClass("swatch_hi");
			$(".swatch").eq(next).addClass("swatch_hi");
			
			$.cookie('mysite_sheetswitch_idx', next, {expires: 7});
		}
		
		return false;
	});
	
	$(".sheetswitch_prev").click(function() {
		var selected = $(".switch[rel='stylesheet']").filter(function () { return $(this).attr("disabled") == false; });
		var current_idx = $(".switch[rel='stylesheet']").index($(selected));
		var length = $(".switch[rel='stylesheet']").size();
		
		if (current_idx >= 0) {
			var next = current_idx - 1;
			if (next == -1) next = (length - 1);
			
			$(".switch[rel='stylesheet']").attr("disabled", "true");
			$(".switch[rel='stylesheet']").eq(next).attr("disabled", "");
			
			$(".swatch").removeClass("swatch_hi");
			$(".swatch").eq(next).addClass("swatch_hi");
			
			$.cookie('mysite_sheetswitch_idx', next, {expires: 7});
		}
		
		return false;
	});
	
	if ($.cookie('mysite_sheetswitch_idx')) {
		var idx = $.cookie('mysite_sheetswitch_idx');
		$(".switch[rel='stylesheet']").eq(idx).attr("disabled", "");
		$(".swatch").eq(idx).addClass("swatch_hi");
	}
});