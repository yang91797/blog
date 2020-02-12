// 头像

$("#avatar").change(function () {
    // 获取用户选中的文件对象
    var file_obj = $(this)[0].files[0];

    // 获取文件对象的路径
    var reader = new FileReader();
    reader.readAsDataURL(file_obj);

    // 修改img的src属性， src=文件对象路径
    reader.onload = function () {
        $("#avatar_img").attr("src", reader.result)
    }
});



//  基于ajax提交数据
$(".reg_btn").click(function () {
   var formdata = new FormData();

   var request_data = $("#form").serializeArray();
   $.each(request_data, function (index, data) {
       formdata.append(data.name, data.value);
   });

   formdata.append("avatar", $("#avatar")[0].files[0]);


   $.ajax({
        url:"",
        type: "post",
        contentType: false,
        processData: false,
        data: formdata,
        success: function (data) {

            if(data.user){
                // 注册成功
                location.href = "/login"
            }else {
                // 先清空错误消息
                $("span.error").html("");
                $(".form-group").removeClass("has-error");

                // 展示此次提交的错误信息
                $.each(data.msg, function (field, error_list) {
                    console.log(field, error_list)
                    if(field=="__all__"){
                        $("#id_re_pwd").next().html(error_list[0]).parent().addClass("has-error");

                    }
                    $("#id_" + field).next().html(error_list[0]);
                    $("#id_" + field).parent().addClass("has-error");   // 错误信息边框变红

                })
            }

        }
    })
});


