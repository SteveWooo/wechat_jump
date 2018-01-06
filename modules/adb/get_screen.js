var exec = require('child_process').exec;

var cap = function(){
	return new Promise(resolve=>{
		exec('adb shell screencap -p ./sdcard/state.png', function(err, data){
			if(err){
				console.log(err);
			}
			resolve();
		})
	})
}

var pull = function(){
	return new Promise(resolve=>{
		exec('adb pull ./sdcard/state.png ' + process.cwd() + '/resources/screen/state.png', function(err, data){
			if(err){
				console.log(err);
			}
			resolve();
		})
	})
}

function get_screen(callback){
	cap().then(result=>{
		return pull();
	}).then(result=>{
		callback && callback();
	})
}

exports.handle = function(){
	return new Promise(resolve=>{
		get_screen(()=>{
			resolve();
		})
	})
}

exports.get_screen = get_screen;