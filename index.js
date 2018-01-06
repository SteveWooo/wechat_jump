var jump = require('./modules/adb/jump').jump;
var get_screen = require('./modules/adb/get_screen').handle;
var getDistence = require('./modules/distence/getDistence').handle;

var main = function(){
	get_screen().then(()=>{
		return getDistence();
	}).then(()=>{
		setTimeout(function(){
			main();
		}, 15000)
	})
}

main();