//Sliding Effect Control
head.js(STATIC_URL + "js/skin-select/jquery.cookie.js");
head.js(STATIC_URL + "js/skin-select/skin-select.js");

//Showing Date
head.js(STATIC_URL + "js/clock/date.js");

//Bootstrap
//head.js(STATIC_URL +"js/bootstrap.js");
head.js(STATIC_URL + "js/bootstrap-modalmanager.js");
head.js(STATIC_URL + "js/bootstrap-modal.js", function () {
    $.fn.modal.defaults.spinner = $.fn.modalmanager.defaults.spinner =
        '<div class="loading-spinner" style="width: 200px; margin-left: -100px;">' +
        '<div class="progress progress-striped active">' +
        '<div class="progress-bar" style="width: 100%;"></div>' +
        '</div>' +
        '</div>';
    $(document).on('click', '.need-modal', function () {
        $('body').modalmanager('loading');
        var $this = $(this);
        setTimeout(function () {
            var href = $this.attr("href");
            alert(href);
            $("#modalContent").load(href + " #load_content", function () {
                $("#modalContent").modal();
            });
        }, 1000);
        return false;
    });

});

head.js(STATIC_URL + "js/datepicker/bootstrap-datepicker.js", function () {
    $("body").delegate(".datepicker", "focusin", function () {
        $(this).datepicker();
    });
});

head.js(STATIC_URL + "js/timepicker/bootstrap-timepicker.js", function () {
    $("body").delegate(".timepicker", "focusin", function () {
        $(this).timepicker({
            minuteStep: 1,
            template: 'modal',
            appendWidgetTo: 'body',
            showSeconds: false,
            showMeridian: false,
            defaultTime: false
        });
    });
});

head.js(STATIC_URL + "js/datepicker/bootstrap-datetimepicker.js", function () {
    $(".datetimepicker").datetimepicker();
});

////Acordion and Sliding menu

head.js(STATIC_URL + "js/custom/scriptbreaker-multiple-accordion-1.js", function () {

    $(".topnav").accordionze({
        accordionze: true,
        speed: 500,
        closedSign: '<img src="' + STATIC_URL + 'img/plus.png">',
        openedSign: '<img src="' + STATIC_URL + 'img/minus.png">'
    });

});

////Right Sliding menu

head.js(STATIC_URL + "js/slidebars/slidebars.min.js", STATIC_URL + "js/jquery.easing.min.js", function () {

    $(document).ready(function () {
        var mySlidebars = new $.slidebars();

        $('.toggle-left').on('click', function () {
            mySlidebars.toggle('right');
        });
    });
});

//-------------------------------------------------------------

//SEARCH MENU
head.js(STATIC_URL + "js/search/jquery.quicksearch.js", function () {

    $('input.id_search').quicksearch('#menu-showhide li, .menu-left-nest li');


});
//-------------------------------------------------------------

//TOOL TIP
//
head.js(STATIC_URL + "js/tip/jquery.tooltipster.js", function () {

    $('.tooltip-tip-x').tooltipster({
        position: 'right'

    });

    $('.tooltip-tip').tooltipster({
        position: 'right',
        animation: 'slide',
        theme: '.tooltipster-shadow',
        delay: 1,
        offsetX: '-12px',
        onlyOne: true

    });
    $('.tooltip-tip2').tooltipster({
        position: 'right',
        animation: 'slide',
        offsetX: '-12px',
        theme: '.tooltipster-shadow',
        onlyOne: true

    });
    $('.tooltip-top').tooltipster({
        position: 'top'
    });
    $('.tooltip-right').tooltipster({
        position: 'right'
    });
    $('.tooltip-left').tooltipster({
        position: 'left'
    });
    $('.tooltip-bottom').tooltipster({
        position: 'bottom'
    });
    $('.tooltip-reload').tooltipster({
        position: 'right',
        theme: '.tooltipster-white',
        animation: 'fade'
    });
    $('.tooltip-fullscreen').tooltipster({
        position: 'left',
        theme: '.tooltipster-white',
        animation: 'fade'
    });
    //For icon tooltip


});
//------------------------------------------------------------- 

//NICE SCROLL

head.js(STATIC_URL + "js/nano/jquery.nanoscroller.js", function () {

    $(".nano").nanoScroller({
        //stop: true 
        scroll: 'top',
        scrollTop: 0,
        sliderMinHeight: 40,
        preventPageScrolling: true
        //alwaysVisible: false

    });

});

//------------------------------------------------------------- 
//PAGE LOADER
head.js(STATIC_URL + "js/pace/pace.js", function () {

    paceOptions = {
        ajax: false, // disabled
        document: false, // disabled
        eventLag: false, // disabled
        elements: {
            selectors: ['.my-page']
        }
    };

});

//DIGITAL CLOCK
head.js(STATIC_URL + "js/clock/jquery.clock.js", function () {

    //clock
    $('#digital-clock').clock({
        offset: '+8',
        type: 'digital'
    });
});

//------------------------------------------------------------- 

head.js(STATIC_URL + "js/gage/raphael.2.1.0.min.js", STATIC_URL + "js/gage/justgage.js", function () {


    var g1;
    window.onload = function () {
        var g1 = new JustGage({
            id: "g1",
            value: getRandomInt(0, 1000),
            min: 0,
            max: 1000,
            relativeGaugeSize: true,
            gaugeColor: "rgba(0,0,0,0.4)",
            levelColors: "#0DB8DF",
            labelFontColor: "#ffffff",
            titleFontColor: "#ffffff",
            valueFontColor: "#ffffff",
            label: "VISITORS",
            gaugeWidthScale: 0.2,
            donut: true
        });
    };


});

head.js(STATIC_URL + "js/iCheck/jquery.icheck.js", function () {

});

head.js(STATIC_URL + "js/common.js", function () {

});

