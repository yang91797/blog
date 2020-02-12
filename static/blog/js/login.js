// 刷新验证码
$('#valid_code_img').click(function () {
    $(this)[0].src += "?"
});

//  滑动验证码
var handlerPopup = function (captchaobj) {

    captchaobj.onSuccess(function () {
        var validate = captchaobj.getValidate();
        $.ajax({
            url: "",    // 进行二次验证
            type: "post",
            dataType: "json",
            data: {
                user: $("#user").val(),
                pwd: $("#pwd").val(),
                geetest_challenge: validate.geetest_challenge,
                geetest_validate: validate.geetest_validate,
                geetest_seccode: validate.geetest_seccode,
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            },
            success: function (data) {
                if (data.user) {
                    console.log(location.search)
                    if (location.search) {
                        location.href = location.search.slice(6)   // 注销时会
                    }
                    else {
                        location.href = "/index"
                    }
                }
                else {
                    $(".error").text(data.msg).css({"color": "red", "margin-left": "10px"});
                }

            }
        })
    });

    $("#popup-submit").click(function () {

        captchaobj.show();
    });
    
    captchaobj.appendTo("#popup-captcha");
    

};


$.ajax({
    url: "/pc-geetest/register?t=" + (new Date().getTime()),
    type: "get",
    dataType: "json",
    success: function (data) {
        initGeetest({
            gt: data.gt,
            challenge: data.challenge,
            product: "popup",
            offline: !data.success
        }, handlerPopup);
    }
});





