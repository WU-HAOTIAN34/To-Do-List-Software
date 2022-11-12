
$(function (){
    if(document.getElementById('demo')!=null){
        layui.use('layedit', function(){
            let layedit = layui.layedit;
            layedit.build('demo');
        });
    }
    if(document.getElementById('description-text')!=null){
        document.getElementById('demo').value=document.getElementById('description-text').placeholder;
        var obj = document.getElementById('description-text');
        obj.remove();
    }
    if(document.getElementById('second')!=null){
        document.getElementById("first").value=''
        document.getElementById("second").value=''
        document.getElementById("release_day").value=''
        document.getElementById("deadline").value=''
        $('#click-btn').click(function (){
            $('input').css('color', 'white')
            if(document.getElementById('second').value===''){
                document.getElementById('second').value="20020930";
            }
            if(document.getElementById('first').value===''){
                document.getElementById('first').value="20020930";
            }
            if(document.getElementById('release_day').value===''){
                document.getElementById('release_day').value = "1902-02-02";
            }
            if(document.getElementById('deadline').value===''){
                document.getElementById('deadline').value = "1902-02-02";
            }
        })
    }
})
