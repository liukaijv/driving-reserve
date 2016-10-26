// 一些公共函数
function getURLVar(key) {
    var value = [];
    var query = String(document.location).split('?');
    if (query[1]) {
        var part = query[1].split('&');
        for (i = 0; i < part.length; i++) {
            var data = part[i].split('=');
            if (data[0] && data[1]) {
                value[data[0]] = data[1];
            }
        }
        if (value[key]) {
            return value[key];
        } else {
            return '';
        }
    }
}

String.prototype.format = function (args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof (args) == "object") {
            for (var key in args) {
                if (args[key] != undefined) {
                    var reg = new RegExp("({" + key + "})", "g");
                    result = result.replace(reg, args[key]);
                }
            }
        }
        else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    var reg = new RegExp("({[" + i + "]})", "g");
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
};


$(function () {
    var csrftoken = $.cookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        cache: false,
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    })
});

var bintSearchEvent = function () {
    var searchBox = $('#searchBox');
    $(document).on('click', '#showSearch', function () {
        var _this = $(this);
        if (searchBox.is(':hidden')) {
            var offRight = _this.offset().left + _this.outerWidth();
            var offBottom = _this.offset().top + _this.outerHeight();
            searchBox.css({
                top: offBottom + 'px',
                left: (offRight - searchBox.outerWidth()) + 'px'
            });
        }
        searchBox.toggle();
    });

    $(document).on('click', function (e) {
        var target = $(e.target);
        if (target.is('#showSearch')) {
            return;
        }
        if (!target.parents('.search-box').andSelf().filter(function () {
                return this === searchBox.get(0)
            }).length) {
            searchBox.hide();
        }
    });
};

var bindCheckBox = function () {
    $('input[type=checkbox]').iCheck({
        checkboxClass: 'icheckbox_flat-red',
        radioClass: 'iradio_flat-red'
    });
    $('[data-role="check-all"]').on('ifChecked', function (event) {
        $(".checkbox").iCheck('check');

    }).on('ifUnchecked', function (event) {
        $(".checkbox").iCheck('uncheck');
    });

    $(".checkbox").on('ifChecked', function () {
        var values = $(".checkedids").val();
        $(".checkedids").val(values + $(this).val() + ',');
    }).on('ifUnchecked', function () {
        var values = $(".checkedids").val();
        var arr = values.split(',');
        var index = arr.indexOf($(this).val());
        arr.splice(index, 1);
        $(".checkedids").val(arr.join(','));
    });
};

function refresh(url) {
    var href = location.href;
    if (url) {
        href = url;
    }
    if (href.indexOf("load") == -1) {
        if (href.indexOf("?") == -1) {
            href = href + "?load=true";
        } else {
            href = href + "&load=true";
        }
    }
    $('.wrap-fluid').load(href + ' #load_content', function () {
        $(this).hide().fadeIn();
        bintSearchEvent();
        bindCheckBox();
    });
}

// 页面加载后运行
$(function () {
    $(document).on('click', '.del-item', function () {
        if (confirm('你确定要删除吗？删除后不可恢复！')) {
            $.post(this.href, function (data) {
                if (data.result == "ok") {
                    window.location.href = window.location.href;
                } else {
                    alert(data.message);
                }
            }).fail(function () {
                alert("系统请求异常。");
            });
        }
        return false;
    });

    // ajax弹框提交
    $(document).on('submit', 'form[data-ajax="true"]', function () {
        $(this).ajaxSubmit(function (data) {
            $('#modal').modal('hide');
        });
        return false;
    });

    // 侧边showSearch菜单状态用sessionStorage，ie8+
    $('.sidebar-nav a[href]').on('click', function () {
        sessionStorage.setItem('side-menu', $(this).attr('href'));
    });
    if (!sessionStorage.getItem('side-menu')) {
        $('.sidebar-nav #dashboard').addClass('active');
    } else {
        $('.sidebar-nav a[href=\'' + sessionStorage.getItem('side-menu') + '\']').addClass('active');
    }

    // 弹出页面
    $(document).on('click', '[data-toggle="page"]', function () {

        var _this = $(this);
        title = _this.attr('title'),
            url = _this.attr('href');
        // 没有页面
        if (!url || /#/.test(url)) {
            return false;
        }

        var pageModal = $('#pageModal');
        if (!pageModal.length) {
            var modalHtml = "";
            modalHtml += "<div class=\"modal fade\" id=\"pageModal\">";
            modalHtml += "  <div class=\"modal-dialog\">";
            modalHtml += "    <div class=\"modal-content\">";
            modalHtml += "      <div class=\"modal-header\">";
            modalHtml += "        <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;<\/span><\/button>";
            modalHtml += "        <h4 class=\"modal-title\">Modal title<\/h4>";
            modalHtml += "      <\/div>";
            modalHtml += "      <div class=\"modal-body\">";
            modalHtml += "        ";
            modalHtml += "      <\/div>    ";
            modalHtml += "    <\/div>";
            modalHtml += "  <\/div>";
            modalHtml += "<\/div>";
            $('body').append(modalHtml);
            pageModal = $('#pageModal');
        }
        var modalHeader = $('.modal-header', pageModal),
            modalBody = $('.modal-body', pageModal);
        title ? modalHeader.find('h4').html(title) : modalHeader.hide();

        $iframe = $('<iframe />');

        $iframe.attr({
            src: url,
            name: "pageModal",
            width: '100%',
            height: '100%',
            allowtransparency: 'yes',
            frameborder: 'no',
            scrolling: 'no'
        }).on('load', function () {
            console.log('loaded');
        });

        modalBody.html($iframe);

        pageModal.modal('show');

        pageModal.on('shown.bs.modal', function (e) {
            modalBody.width($iframe.contents().width());
            modalBody.height($iframe.contents().height());
            pageModal.modal('handleUpdate');
        });

        pageModal.on('hidden.bs.modal', function (e) {
            $iframe.attr('src', 'about:blank').remove();
            pageModal.remove();
        });

        return false;

    });

    $(document).on('click', '[data-dismiss="page"]', function () {
        parent.$('#pageModal').modal('hide');
    });

    bintSearchEvent();
    bindCheckBox();


    $(document).on('click', '.ajax-load', function () {
        var href = $(this).attr('href');

        if (href.indexOf("load") == -1) {
            if (href.indexOf("?") == -1) {
                href = href + "?load=true";
            } else {
                href = href + "&load=true";
            }
        }
        window.history.pushState({}, 0, href);
        $('.wrap-fluid').load(href + ' #load_content', function () {
            $(this).hide().fadeIn();
            bintSearchEvent();
            bindCheckBox();
        });
        $("html,body").animate({scrollTop: 0}, 200);
        return false;
    });
});