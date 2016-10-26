window.addEventListener('load', function () {
    setTimeout(function () {
        window.scrollTo(0, 1);
    }, 100);
});

function hideAddressBar_android() {
    var self = document.getElementsByTagName('body')[0];
    if (self.requestFullscreen) {
        //html5新增的全屏方法
        self.requestFullscreen();
    } else if (self.mozRequestFullScreen) {
        //针对mozlia内核的hack
        self.mozRequestFullScreen();
    } else if (self.webkitRequestFullScreen) {
        //针对webkit内核的hack
        self.webkitRequestFullScreen();
    }
};

// init App
var App = new Framework7({
    modalTitle: '提示信息',
    animateNavBackIcon: true,
    modalButtonOk: '确定',
    modalButtonCancel: '取消',
    pushState: true
});

var $$ = Dom7;

// getCookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function crossDomain(url) {
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var mainView = App.addView('.view-main', {
    dynamicNavbar: true,
});

$$(document).on('ajaxStart', function (e) {
    var xhr = e.detail.xhr;
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    App.showIndicator();
});
$$(document).on('ajaxComplete', function () {
    App.hideIndicator();
});

$$('#logout').click(function (e) {
    App.closeModal('.popover-menu');
    var me = $$(this);
    App.confirm('确定要退出登陆吗？', function () {
        window.location.href = me.attr('href');
    }, function () {
    });
    e.preventDefault();
});


$(function () {

    $(document).on('ajaxStart', function () {
        App.showIndicator();
    });
    $(document).on('ajaxComplete', function () {
        App.hideIndicator();
    });

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('[data-role="ajax-validate"]').ajax_validate({
        submitHandler: function () {
            var form = $(this),
                postData = form.serialize(),
                url = form.attr('action');
            $.post(url, postData, function (result) {
                if (result.msg) {
                    App.alert(result.msg, function () {
                        form.get(0).reset();
                        if (result.next) {
                            window.location.href = result.next;
                        }
                    });
                    return false;
                }
                if (result.next) {
                    window.location.href = result.next;
                }
            });
            return false;
        }
    });

    $(document).on('click', '.msg-item', function () {

        if ($('.msg-picker-modal.modal-in').length > 0) {
            App.closeModal('.msg-picker-modal.modal-in');
        }

        var id = $(this).attr('data-id');

        if (!id) {
            return false;
        }

        var markRead = $(this).find('[data-read]').attr('data-read');

        if (id && markRead == 'false') {
            $.post('/app/message_view/', {id: id}, function (data) {
                var message = JSON.parse(data.json_data);
                var popupHTML = '<div class="popup popup-msg">' +
                    '<div class="navbar">' +
                    '<div class="navbar-inner">' +
                    '<div class="left">' + '<a href="#" class="close-popup">关闭</a>' +
                    '</div>' +
                    '<div class="center"></div>' +
                    '<div class="right ">' + '<a href="#" data-id="' + id + '" class="msg-delete">删除</a>' +
                    '</div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="content-block">' +
                    message[0].fields.send_content +
                    '</div>' +
                    '</div>';
                App.popup(popupHTML);
                $('.msg-item[data-id="' + id + '"]').find('.badge').removeClass('bg-orange').text('已读');
                $('.msg-item[data-id="' + id + '"]').find('[data-read]').attr('data-read', 'true');
            });
        } else {
            var text = $(this).find('.item-text').text();
            var popupHTML = '<div class="popup popup-msg">' +
                '<div class="navbar">' +
                '<div class="navbar-inner">' +
                '<div class="left">' + '<a href="#" class="close-popup">关闭</a>' +
                '</div>' +
                '<div class="center"></div>' +
                '<div class="right ">' + '<a href="#" data-id="' + id + '" class="msg-delete">删除</a>' +
                '</div>' +
                '</div>' +
                '</div>' +
                '<div class="content-block">' +
                text +
                '</div>' +
                '</div>';
            App.popup(popupHTML);
            return false;
        }

    });

    $(document).on('click', '.msg-delete', function () {
        App.closeModal('.msg-picker-modal.modal-in');
        var id = $(this).attr('data-id');
        if (id) {
            App.confirm('确定要删除此消息吗？', function () {
                $.post('/app/message_delete/', {id: id}, function (result) {
                    App.alert(result.msg, function () {
                        if (result.next) {
                            window.location.href = result.next;
                        }
                    });
                });
            });
        }
    })

    $(document).on('click', '#reserve-action', function () {
        var checkItem = $('[name="train_time_span"]:checked');
        if (!checkItem.length) {
            App.alert('请先选择预约时间段');
            return false;
        }
        App.confirm('确定要预约此时间段吗？', function () {
            var train_time_span = checkItem.val(),
                train_date = $('[name="train_time_span"]:checked').closest('li').find('[name="train_date"]').val(),
                data = {train_time_span_id: train_time_span, train_date: train_date};
            $.ajax({
                url: '/app/confirm_order_condition/',
                data: data,
                type: 'POST',
                dataType: 'json',
                success: function (result) {
                    App.alert(result.msg, function () {
                        if (result.next) {
                            window.location.href = result.next;
                        }
                    });
                }
            });
        });

    });

    $(document).on('click', '.show-reserve-detail', function () {
        var html = $(this).find('[data-block="detail"]').html();
        var popupHTML = '<div class="popup popup-order">' +
            '<div class="navbar">' +
            '<div class="navbar-inner">' +
            '<div class="left">' +
            '<a href="#" class="close-popup">返回</a>' +
            '</div>' +
            '<div class="center"></div>' +
            '<div class="right ">' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="content-block-title">预约详情</div>' +
            html +
            '<div class="content-block">' +
            '<a href="#" class="button button-big close-popup">返回</a>' +
            '</div>' +
            '</div>';
        App.popup(popupHTML);
    });

    $(document).on('click', '.disable-tip', function () {
        var clickedLink = this;
        var msg = $(this).attr('data-msg');
        var popoverHTML = '<div class="popover">' +
            '<div class="popover-inner">' +
            '<div class="content-block">' +
            msg +
            '</div>' +
            '</div>' +
            '</div>'
        App.popover(popoverHTML, clickedLink);
    });

    $(document).on('click', '.do-actions', function (e) {
        var _this = $(this);
        var id = _this.attr('id');
        var actionSheetButtons = [
            [
                {
                    text: '请选择你要进行的操作',
                    label: true
                },
                {
                    text: '已到',
                    onClick: function () {
                        App.confirm('签到后不能再次更改，确定要进行些操作吗？', function () {
                            $.post('/app/change_sign_status/', {'id': id, 'sign_status': 1}, function (result) {
                                App.alert(result.msg, function () {
                                    if (result.sign_status == 1) {
                                        _this.addClass('color-gray').removeClass('color-red').removeClass('do-actions').text('已到');
                                    }
                                });
                            });
                        });
                    }
                },
                {
                    text: '未到 ',
                    color: 'red',
                    onClick: function () {
                        App.confirm('签到后不能再次更改，确定要进行些操作吗？', function () {
                            $.post('/app/change_sign_status/', {'id': id, 'sign_status': -1}, function (result) {
                                App.alert(result.msg, function () {
                                    if (result.sign_status == -1) {
                                        _this.addClass('color-gray').removeClass('color-blue').removeClass('do-actions').text('未到');
                                    }
                                });
                            });
                        });
                    }
                },
            ],
            [
                {
                    text: '取消',
                    bold: true
                }
            ]
        ];

        App.actions(actionSheetButtons);

        return false;
    });

    var toTop = $('#toTop');
    $(".page-content").on('scroll', function () {
        if ($(this).scrollTop() >= 100) {
            toTop.fadeIn();
        } else {
            toTop.fadeOut();
        }
    });
    toTop.on('click', function () {
        console.log(1);
        $(".page-content").animate({scrollTop: 0}, 100);
        return false;
    });

});

var init_page = 1;
var loading = false;
$$('.infinite-scroll').on('infinite', function () {
    var preloader = $$('.infinite-scroll-preloader').show();
    var url = $$(this).attr('data-url');
    if (loading) return;
    loading = true;
    $.get(url, {'page': init_page}, function (data) {
        loading = false;
        if ($.trim(data) == '') {
            App.detachInfiniteScroll($$('.infinite-scroll'));
            preloader.html('没有更多数据了');
            return;
        }
        $$('.infinite-block').append(data);
        preloader.hide();
        init_page++;
    });
}).trigger('infinite');

(function ($) {

    function inputs(form) {
        return form.find(":input:visible:not(:button)");
    }

    $.fn.ajax_validate = function (settings) {

        settings = $.extend({
            url: '',
            callback: false,
            fields: false,
            dom: this,
            event: 'submit',
            submitHandler: null
        }, settings);

        return this.each(function () {

            var form = $(this);
            var url = form.attr('data-url') || settings.url;
            settings.dom.bind(settings.event, function () {
                //debugger;
                var status = false;
                var data = form.serialize();
                if (settings.fields) {
                    data += '&' + $.param({fields: settings.fields, form_class: backendForm});
                }
                $.ajax({
                    async: false,
                    data: data,
                    dataType: 'json',
                    traditional: true,
                    error: function (XHR, textStatus, errorThrown) {
                        status = false;
                    },
                    success: function (data, textStatus) {

                        status = data.valid;
                        if (!status) {
                            if (settings.callback) {
                                settings.callback(data, form);
                            }
                            else {
                                var get_form_error_position = function (key) {
                                    key = key || '__all__';
                                    if (key == '__all__') {
                                        var filter = ':first';
                                    } else {
                                        var filter = ':first[id^=id_' + key.replace('__all__', '') + ']';
                                    }
                                    return inputs(form).filter(filter).parent();
                                };
                                $.each(data.errors, function (key, val) {
                                    if (key.indexOf('__all__') >= 0) {
                                        var error = get_form_error_position(key);
                                    }
                                    else {
                                        //App.closeNotification('.validate-notifications');
                                        App.addNotification({
                                            title: '验证提示',
                                            message: val,
                                            additionalClass: 'validate-notifications',
                                            hold: 5000,
                                            closeIcon: false,
                                            onClick: function () {
                                                App.closeNotification('.validate-notifications');
                                            }
                                        });
                                    }
                                });
                            }
                        }
                    },
                    type: 'POST',
                    url: url
                });
                if (status && settings.submitHandler) {
                    return settings.submitHandler.apply(this);
                }
                return status;
            });
        });
    };
})(jQuery);

(function ($) {
    function Tabs(element, options) {
        this.$element = $(element);
        this.options = $.extend({}, Tabs.DEFAULTS, options || {});
        this.$tabNav = this.$element.find(this.options.selector.nav);
        this.$navs = this.$tabNav.find('a');
        this.$content = this.$element.find(this.options.selector.content);
        this.$tabPanels = this.$content.find(this.options.selector.panel);
        this.transitioning = false;
        this.init()
    };
    Tabs.DEFAULTS = {
        selector: {
            nav: '.tabs-nav',
            content: '.tabs-content',
            panel: '.tabs-panel'
        },
        className: {
            active: 'ui-active'
        },
        swipe: true

    };
    Tabs.prototype = {

        init: function () {
            var me = this;
            var options = this.options;
            if (this.$tabNav.find('> .ui-active').length !== 1) {
                var $tabNav = this.$tabNav;
                this.
                    activate($tabNav.children('li').first(), $tabNav);
                this.activate(this.$tabPanels.first(), this.$content)
            }
            this.$navs.on('click.tabs.ui', function (e) {
                e.preventDefault();
                me.open($(this))
            });
            if (options.swipe) {
                var hammer = new Hammer(this.$content[0]);
                hammer.get('pan').set({
                    direction: Hammer.DIRECTION_HORIZONTAL,
                    threshold: 50
                });
                hammer.on('swipeleft', $.debounce(function (e) {
                    e.preventDefault();
                    var $target = $(e.target);
                    if (!$target.is(options.selector.panel)) {
                        $target = $target.closest(options.selector.panel)
                    }
                    $target.focus();
                    var $nav = me.getNextNav($target);
                    $nav && me.open($nav)
                }, 50));
                hammer.on('swiperight', $.debounce(function (e) {
                    e.preventDefault();
                    var $target = $(e.target);
                    if (!$target.is(options.selector.panel)) {
                        $target = $target.closest(options.selector.panel)
                    }
                    var $nav = me.getPrevNav($target);
                    $nav && me.open($nav)
                }, 50))
            }
        },
        open: function ($nav) {
            if (!$nav || this.transitioning || $nav.parent('li').hasClass('ui-active')) {
                return
            }
            var $tabNav = this.$tabNav;
            var $navs = this.$navs;
            var $tabContent = this.$content;
            var href = $nav.attr('href');
            var regexHash = /^#.+$/;
            var $target = regexHash.test(href) && this.$content.find(href) || this.$tabPanels.eq($navs.index($nav));
            var previous = $tabNav.find('.ui-active a')[0];
            var e = $.Event('open.tabs.ui', {
                relatedTarget: previous
            });
            $nav.trigger(e);
            if (e.isDefaultPrevented()) {
                return
            }
            this.activate($nav.closest('li'), $tabNav);
            this.activate($target, $tabContent, function () {
                $nav.trigger({
                    type: 'opened.tabs.ui',
                    relatedTarget: previous
                })
            })
        },
        activate: function ($element, $container, callback) {
            this.transitioning = true;
            var $active = $container.find('> .ui-active');
            var transition = callback && $.support.transition && !!$active.length;
            $active.removeClass('ui-active');
            $element.width();
            $element.addClass('ui-active');
            if (transition) {
                $active.one($.support.transition.end, function () {
                    callback && callback()
                })
            } else {
                callback && callback()
            }
            this.transitioning = false
        },
        getNextNav: function ($panel) {
            var navIndex = this.$tabPanels.index($panel);
            var rightSpring = 'animation-right-spring';
            if (navIndex + 1 >= this.$navs.length) {
                animation && $panel.addClass(rightSpring).on(animation.end, function () {
                    $panel.removeClass(rightSpring)
                });
                return null
            } else {
                return this.$navs.eq(navIndex + 1)
            }
        },
        getPrevNav: function ($panel) {
            var navIndex = this.$tabPanels.index($panel);
            var leftSpring = 'animation-left-spring';
            if (navIndex === 0) {
                animation && $panel.addClass(leftSpring).on(animation.end, function () {
                    $panel.removeClass(leftSpring)
                });
                return null
            } else {
                return this.$navs.eq(navIndex - 1)
            }
        }
    }

    $.fn.tabs = function (option) {
        return this.each(function () {
            var $this = $(this);
            var $tabs = $this.is('.tabs') && $this || $this.closest('.tabs');
            var data = $tabs.data('ui.tabs');
            var options = $.extend({}, $.isPlainObject(option) ? option : {});
            if (!data) {
                $tabs.data('ui.tabs', (data = new Tabs($tabs[0], options)))
            }
            if (typeof option == 'string' && $this.is('.tabs-nav a')) {
                data[option]($this)
            }
        });
    }
})(jQuery);

$(function () {
    $('.tabs').tabs()
});

$.support.transition = (function () {
    var transitionEnd = (function () {
        var element = window.document.body || window.document.documentElement;
        var transEndEventNames = {
            WebkitTransition: 'webkitTransitionEnd',
            MozTransition: 'transitionend',
            OTransition: 'oTransitionEnd otransitionend',
            transition: 'transitionend'
        };
        var name;
        for (name in transEndEventNames) {
            if (element.style[name] !== undefined) {
                return transEndEventNames[name]
            }
        }
    })();
    return transitionEnd && {
            end: transitionEnd
        }
})();

$.debounce = function (func, wait, immediate) {
    var timeout;
    return function () {
        var context = this;
        var args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) {
                func.apply(context, args);
            }
        };
        var callNow = immediate && !timeout;

        clearTimeout(timeout);
        timeout = setTimeout(later, wait);

        if (callNow) {
            func.apply(context, args);
        }
    };
};