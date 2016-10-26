$$('form.ajax-submit').on('submitted', function (e) {

  var xhr = e.detail.xhr;  
  var result = JSON.parse(e.detail.data);   
  var data = result.data;
  if (result.code == 0 ) {
  	App.alert(result.msg, '登陆错误');
  };
  if (result.code == -1 ) {
  	window.location.href = data.next;
  };
  
});

$$('form.ajax-submit').on('beforeSubmit', function (e) {  

});