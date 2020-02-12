// 点赞
$("#div_digg .action").click(function () {
    var is_up = $(this).hasClass("diggit");
    $obj = $(this).children("span");

    $.ajax({
        url: "/digg/",
        type: "post",
        data: {
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
            "is_up": is_up,
            "article_id": $('#article_id').attr('article_id'),
        },

        success: function (data) {
            console.log(data)
            if (data.state) {
                var val = parseInt($obj.text());
                $obj.text(val + 1)
            } else {
                var val = data.handled ? "您已经推荐过！" : "您已经反对过！";
                $("#digg_tips").html(val);
                setTimeout(function () {
                    $("#digg_tips").html("")
                }, 2000)
            }

        }
    })
});


// 评论树
$.ajax({
    url: "/get_comment_tree/",
    type: "get",
    data: {
        article_id: $('#article_id').attr('article_id'),
    },
    success: function (comment_list) {

        $.each(comment_list, function (index, data) {
            var pk = data.pk;
            var content = data.content;
            var parent_comment_id = data.parent_comment_id;
            var avatar = data.user__avatar;
            var username = data.user__username;
            var create_time = data.create_time.replace('T', ' ').slice(0, 16);
            var parent_avatar = data.parent_comment__user__avatar
            var parent_username = data.parent_comment__user__username

            var tag = `
            <div content_id="${pk}" class="comm_list">
                <a href="/${username}" class="user_mess">
                    <img src="media/${avatar}" alt="头像" width="20px" height="20px" style="border-radius: 50%">
                    <span>${username}</span>:  
                  </a> 
                    回复   
                  <a href="/${parent_username}">
                    <img src="media/${parent_avatar}" alt="头像" width="20px" height="20px" style="border-radius: 50%">
                    <span>${parent_username}</span>
                   </a>
                    <span class="comment_item">${content}</span>
                    <div class="precise">
                        <span class="user_mess">${create_time}</span>
                    <a href="javascript:;" class="reply_son" comment_pk="${pk}" username="${username}">回复</a>
</div>

</div>
              


            `

             $("[content_id=" + parent_comment_id + "]").append(tag);
        })

    }
});

// 评论树提交评论
var pid = "";
$(".btn_tree").click(function () {
    var content = $("#comment_content").val();
    if (pid){
        var index = content.indexOf("\n");
        content = content.slice(index +1)
    }
    $.ajax({
        url: "/get_comment_tree/",
        type: "post",
        data: {
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
            article_id: $('#article_id').attr('article_id'),
            content: content,
            pid: pid
        },
        
        success: function (data) {
            var create_time = data.create_time;
            var username = data.username;
            var content = data.content;
            var username_avatar = data.username_avatar;
            var parent_user = data.parent_user;
            var parent_avatar = data.parent_avatar;
            var parent_id = data.parent_id;

            if(username == null){
                location.href = "/login"
                return
            }
            var pk = data.pk;

            if (parent_user){
                var tag = `
                <div content_id="${pk}" class="comm_list">
                <a href="/${username}" class="user_mess">
                    <img src="media/${username_avatar}" alt="头像" width="20px" height="20px" style="border-radius: 50%">
                    <span>${username}</span>:  
                  </a> 
                    回复   
                  <a href="/${parent_user}">
                    <img src="media/${parent_avatar}" alt="头像" width="20px" height="20px" style="border-radius: 50%">
                    <span>${parent_user}</span>
                   </a>
                    <span class="comment_item">${content}</span>
                    <div class="precise">
                        <span class="user_mess">${create_time}</span>
                    <a href="javascript:;" class="reply_son" comment_pk="${pk}" username="${username}">回复</a>
</div>

</div>
              
                
                `
        $("[content_id=" + parent_id + "]").append(tag);
            }else {
                var tag = `
                <div content_id="${pk}" class="comm_list">
                        <a href="" class="user_mess">
                            <img src="media/${username_avatar}" alt="头像" width="20px" height="20px" style="border-radius: 50%">
                            <span>${username}</span>
                        </a>
                        <span class="comment_item">${content}</span>
                        <div class="precise">
                            <span class="user_mess">${create_time}</span>
                            <a href="javascript:;" class="reply_btn" comment_pk="${pk}" username="${username}">回复</a>
                        </div>

                    </div>
                    <hr>
                
                
                
                `
                $(".comment_tree").append(tag)
            }


            pid = "";
            $("#comment_content").val("");
        }
    })
})

//回复： 使用事件代理

$(".comment_tree").on('click', '.reply_son, .reply_btn', function () {
    $("#comment_content").focus();
    var val = "@" + $(this).attr("username") + "\n";
    $("#comment_content").val(val);

    pid = $(this).attr("comment_pk");

})
