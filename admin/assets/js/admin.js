//后台使用
var reserve = {
    post_action: function (actionName) {
        var reserveid = $("#reserveid").val();
        var remarks = $("#remarks").val();
        $.post("/admin/drive/check/",
            {
                "id": reserveid,
                "type": actionName,
                "remarks": remarks
            },
            function (data) {
                if (data.code == 0) {
                    $(".alert").html('操作成功!').focus();
                    window.location.href = "/admin/drive/list/";
                }
            });
    },
    pass: function () {
        this.post_action("pass");
    },
    refuse: function () {
        this.post_action("refuse");
    },
    check_reserve: function (obj) {
        var url = $("#form_reserve").attr("action");
        var data = $("#form_reserve").serialize();
        var result = false;
        $.ajax({
            type: "post",
            url: url,
            data: data,
            async: false,
            success: function (data) {
                if (data.result == "ok") {
                    $(".alert").html('操作成功!').focus();
                    result = true;
                } else {
                    alert(data.result);
                }
            }
        });
        return result;
    },
    batch_delete: function (obj) {
        var $this = $(obj);
        var href = $this.attr("href");
        var ids = $(".checkedids").val();
        if (ids.length == 0) {
            alert('请先勾选需要删除的记录!');
            return false;
        }
        if (confirm('你确定要删除勾选的预约记录吗？')) {
            $.post(href, {ids: ids}, function (result) {
                if (result.code == 1) {
                    refresh();
                } else {
                    alert(result.message);
                }
            });
        }
        return false;
    },
    batch_audit: function (obj) {
        var $this = $(obj);
        var href = $this.attr("href");
        var ids = $(".checkedids").val();
        if (ids.length == 0) {
            alert('请先勾选需要审核的记录!');
            return false;
        }
        if (confirm('要审核通过吗？审核通过会自动发送短信')) {
            $.post(href, {ids: ids}, function (result) {
                if (result.code == 0) {
                    refresh();
                } else {
                    alert(result.msg);
                }
            });
        }
        return false;
    }
};
var exam = {
    post_action: function (actionName) {
        var reserveid = $("#reserveid").val();
        var remarks = $("#remarks").val();
        $.post("/admin/exam/check/",
            {
                "id": reserveid,
                "type": actionName,
                "remarks": remarks
            },
            function (data) {
                if (data.code == 0) {
                    $(".alert").html('操作成功!').focus();
                    window.location.href = "/admin/exam/list/";
                }
            });
    },
    pass: function () {
        this.post_action("pass");
    },
    refuse: function () {
        this.post_action("refuse");
    },
    batch_delete: function (obj) {
        var $this = $(obj);
        var href = $this.attr("href");
        var ids = $(".checkedids").val();
        if (ids.length == 0) {
            alert('请先勾选需要删除的记录!');
            return false;
        }
        if (confirm('你确定要删除勾选的预约记录吗？')) {
            $.post(href, {ids: ids}, function (result) {
                if (result.code == 0) {
                    refresh();
                } else {
                    alert(result.msg);
                }
            });
        }
        return false;
    },
    batch_audit: function (obj) {
        var $this = $(obj);
        var href = $this.attr("href");
        var ids = $(".checkedids").val();
        if (ids.length == 0) {
            alert('请先勾选需要审核的记录!');
            return false;
        }
        if (confirm('要审核通过吗？审核通过会自动发送短信')) {
            $.post(href, {ids: ids}, function (result) {
                if (result.code == 0) {
                    refresh();
                } else {
                    alert(result.msg);
                }
            });
        }
        return false;
    }
};
var user = {
    change_status: function (obj) {
        $this = $(obj);
        user_id = $("#user_id").val();
        stage_status = $("#stage_status").val();
        if (confirm('你要更新该学员的状态吗？更新完成会发送短信')) {
            $.post('/admin/user/modify/changestatus/', {userid: user_id, status: $this.val()}, function (data) {
                if (data.result == "Ok") {
                    alert('操作成功');
                } else {
                    alert(data.result);
                }
            });
        } else {
            $this.val(stage_status)
        }
    }
};
var car = {
    check_days: function () {
        $stage_twos = $("input[name=stage_two_train_time]:checked");
        $stage_threes = $("input[name=stage_three_train_time]:checked");
        var ret = true;
        $stage_twos.each(function () {
            var value = $(this).val();
            $stage_threes.each(function () {
                var three_value = $(this).val();
                if (value == three_value) {
                    alert("科目二和科目三不能有重复的训练时间。");
                    ret = false;
                    return false;
                }
            });
        });
        return ret;
    }
};
var sms = {
    batch_delete: function(obj) {
        var $this = $(obj);
        var href = $this.attr("href");
        var ids = $(".checkedids").val();
        if (ids.length == 0) {
            alert('请先勾选需要删除的记录!');
            return false;
        }
        if (confirm('你确定要删除勾选的预约记录吗？')) {
            $.post(href, {ids: ids}, function (result) {
                if (result.code == 0) {
                    refresh();
                } else {
                    alert(result.msg);
                }
            });
        }
        return false;
    }
};