$$('form.ajax-submit').on('submitted', function (e) {

  // var xhr = e.detail.xhr;  
  // var result = JSON.parse(e.detail.data);   
  // var data = result.data;
  // if (result.code == -1 ) {
  // 	App.alert(result.msg, '登陆错误');
  // };  
  
});

$$('form.ajax-submit').on('beforeSubmit', function (e) { 
	var xhr = e.detail.xhr; 
	console.log(xhr);
	App.confirm('确定要提投诉吗？', function(){}, function(){
		xhr.abort();
		return false;
	});
});