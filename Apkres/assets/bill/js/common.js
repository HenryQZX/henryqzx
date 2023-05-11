//打开字滑入效果
window.onload = function(){
	$(".connect p").eq(0).animate({"left":"0%"}, 600);
	$(".connect p").eq(1).animate({"left":"0%"}, 400);
};
//jquery.validate表单验证
$(document).ready(function(){
	//登陆表单验证
	$("#loginForm").validate({
		rules:{
			username:{
				required:true,//必填
				minlength:3, //最少6个字符
				maxlength:32,//最多20个字符
			},
			password:{
				required:true,
				minlength:3, 
				maxlength:32,
			},
			xieyi:{
			    required:true,
			},
		},
		//错误信息提示
		messages:{
			username:{
				required:"Username must be filled in",
				minlength:"At least 3 characters",
				maxlength:"Up to 32 characters",
				remote: "Username occupied",
			},
			password:{
				required:"Password must be filled in",
				minlength:"At least 3 characters",
				maxlength:"Up to 32 characters",
			},
			xieyi:{
			    required:"You must agree to the user agreement!",
			},
		},

	});
	//注册表单验证
	$("#regForm").validate({
		rules:{
			username:{
				required:true,//必填
				minlength:3, //最少6个字符
				maxlength:32,//最多20个字符

			},
			password:{
				required:true,
				minlength:3, 
				maxlength:32,
			},
			email:{
				required:true,
				email:true,
			},
			confirm_password:{
				required:true,
				minlength:3,
				equalTo:'.password'
			},
			xieyi:{
			    required:true,
			},
		},
		//错误信息提示
		messages:{
			username:{
				required:"Username must be filled in",
				minlength:"At least 3 characters",
				maxlength:"Up to 32 characters",
				remote: "Username occupied",
			},
			password:{
				required:"Password must be filled in",
				minlength:"At least 3 characters",
				maxlength:"Up to 32 characters",
			},
			email:{
				required:"your email address is required",
				email: "Pls correct email address"
			},
			confirm_password:{
				required: "Pls enter your password again.",
				minlength: "At least 3 characters",
				equalTo: "Two inconsistent passwords",//与另一个元素相同
			},
			xieyi:{
			    required:"You must agree to the user agreement!",
			},
		
		},
	});

});
