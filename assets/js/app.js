//BACKGROUND CHANGER

$(function () {
    var background_url = "";
    $("#button-bg").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg5.jpg')no-repeat center center fixed";
        change_background(background_url);
    });

    $("#button-bg2").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg2.jpg')no-repeat center center fixed";
        change_background(background_url);
    });

    $("#button-bg3").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg.jpg')no-repeat center center fixed";
        change_background(background_url);
    });

    $("#button-bg5").click(function () {
        background_url = "url('" + STATIC_URL + "img/giftly.png')repeat";
        change_background(background_url);
    });

    $("#button-bg6").click(function () {
        background_url = "#2c3e50";
        change_background(background_url);
    });

    $("#button-bg7").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg3.png')repeat";
        change_background(background_url);
    });

    $("#button-bg8").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg8.jpg')no-repeat center center fixed";
        change_background(background_url);
    });

    $("#button-bg9").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg9.jpg')no-repeat center center fixed";
        change_background(background_url);

    });

    $("#button-bg10").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg10.jpg')no-repeat center center fixed";
        change_background(background_url);

    });
    $("#button-bg11").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg11.jpg')no-repeat center center fixed";
        change_background(background_url);

    });
    $("#button-bg12").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg12.jpg')no-repeat center center fixed";
        change_background(background_url);
    });

    $("#button-bg13").click(function () {
        background_url = "url('" + STATIC_URL + "img/bg13.jpg')repeat";
        change_background(background_url);
    });
    /**
     * Background Changer end
     */
});

function change_background(url) {
    $.cookie('bkground', url, { path : '/'});
    $("body").css({
        "background": url
    });
}

//TOGGLE CLOSE
$('.nav-toggle').click(function () {
    //get collapse content selector
    var collapse_content_selector = $(this).attr('href');

    //make the collapse content to be shown or hide
    var toggle_switch = $(this);
    $(collapse_content_selector).slideToggle(function () {
        if ($(this).css('display') == 'block') {
            //change the button label to be 'Show'
            toggle_switch.html('<span class="entypo-minus-squared"></span>');
        } else {
            //change the button label to be 'Hide'
            toggle_switch.html('<span class="entypo-plus-squared"></span>');
        }
    });
});


$('.nav-toggle-alt').click(function () {
    //get collapse content selector
    var collapse_content_selector = $(this).attr('href');

    //make the collapse content to be shown or hide
    var toggle_switch = $(this);
    $(collapse_content_selector).slideToggle(function () {
        if ($(this).css('display') == 'block') {
            //change the button label to be 'Show'
            toggle_switch.html('<span class="entypo-up-open"></span>');
        } else {
            //change the button label to be 'Hide'
            toggle_switch.html('<span class="entypo-down-open"></span>');
        }
    });
    return false;
});
//CLOSE ELEMENT
$(".gone").click(function () {
    var collapse_content_close = $(this).attr('href');
    $(collapse_content_close).hide();


});

//tooltip
$('.tooltitle').tooltip();
 