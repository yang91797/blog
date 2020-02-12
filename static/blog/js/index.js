// 点赞
$(".up").each(function () {
    $(this).click(function () {
        var diggit = $(this).children("i");
        var span = $(this).next();

        $.ajax({
            url: "/digg/",
            type: "post",
            data:{
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
                "is_up": true,
                "article_id": $(this).attr('article_id'),
            },

            success: function (data) {
                console.log(data);
                if (data.state){
                    var count = data.up_count;
                    if(count){
                        diggit.text("点赞("+count+")")
                    }

                }else {
                    var val = data.handled ? "您已经推荐过！" : "您已经反对过！";

                    span.html(val);
                    setTimeout(function () {
                        span.html("")
                    }, 2000)
                }

            }
        })
    })
});

