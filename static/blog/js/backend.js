$('.cancel').click(function(){
    $(".shade").addClass("hide")
    $(".models").addClass("hide")

});

$(".delete").click(function () {
    $(".shade").removeClass("hide");
    $(".models").removeClass("hide");
    var url = $(this).attr("url");

    $(".ok").click(function () {
        $.ajax({
            url: url,

                success: function (data) {
                if (data == "ok"){
                    location.reload()
                }
        }
        },


        )
    })

});
