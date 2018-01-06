var exec = require('child_process').exec;

function jump(distence, callback){
	exec('adb shell input swipe 900 900 900 900 ' + distence, function(data, err){
		callback && callback();
	})
}

exports.jump = jump;