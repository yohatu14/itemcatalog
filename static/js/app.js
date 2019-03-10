$(document).ready(function(){
    console.log("jnlnjh,vhjkl")
    function ajax_login(){

        $.ajax({
            url:'/ajax-login',
            data: $('form').serialize(),
            type:'POST',
            success: function(response){
                var json=JSON.parse(response)
                console.log(json.redirect);
                window.location.href=json.redirect
            },
            error: function(error){
                console.log(error)
                var json=JSON.parse(response)
                console.log(json.redirect);
                window.location.href=json.redirect
            }
        })

    }

    $("#login-Form").submit(function(event){
        event.preventDefault();
        ajax_login()
    })
})