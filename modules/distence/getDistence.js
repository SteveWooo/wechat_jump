var exec = require('child_process').exec;
var getDistence = function(callback){
	exec('python ' + __dirname + '/main.py', function(err, data){
		if(err){
			console.log(err);
		}
		var stdout = data.replace('\n', '');
		console.log(stdout);
		callback && callback();
	})
}

exports.handle = function(){
	return new Promise(resolve=>{
		getDistence(()=>{
			resolve();
		})
	})
}

exports.getDistence = getDistence;