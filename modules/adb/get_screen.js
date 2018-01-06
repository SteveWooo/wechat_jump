var exec = require('child_process').exec;

var cap = function(){
	return new Promise(resolve=>{
		exec('adb shell screencap -p ./sdcard/p.png', function(data, err){
			resolve();
		})
	})
}

var pull = function(){
	return new Promise(resolve=>{
		exec('adb pull ./sdcard/p.png ' + process.cwd() + '/resources/screen/p.png', function(data, err){
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

exports.get_screen = get_screen;