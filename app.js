var app = require("express")();
var CORS = require('cors')();
var http = require('http').Server(app);
var utils = require('date-utils');
var bodyParser = require('body-parser');
var greeting = "say hello!";
var prev_X = 0;
var prev_Y = 0;
var _time = 1;
var x = 0;
var prev_dist = 0;
var pres_dist = 0;
var max_ax = 0;
var max_ay = 0;
var global_x = 0;
var global_y = 0;
var global_dist = 0;
var global_angle = 0;
var integral = function(f, a, b){
	var area = 0;
	var dx = 0.01;
	for(x = a; x < b; x += dx){
		area += dx * f;
	}
	return area;
}

app.use(bodyParser.json())
app.use(CORS);
app.post('/', function(req, res, next){
	//console.log('req.body.ax type is ', typeof(req.body.ax))
	var start = new Date();
	res.header('Access-Control-Allow-Origin', '*');
	res.header('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS');
	res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Length, X-Requested-With');	
	if(typeof(req.body.ax) != 'undefined'){
	_time = _time + 1;
	console.log('////////////////////////////////////////////////\n');
	console.log('time is : ', _time);
	//console.log("ax, ay, az : " , req.body.ax, req.body.ay, req.body.az);
	//console.log("gx, gy, gz : " , req.body.gx, req.body.gy, req.body.gz);
	//console.log("mx, my, mz : " , req.body.mx, req.body.my, req.body.mz); 
	//console.log('start time is : %d ms ' , new Date() - start);
	console.log('/////////////////////////////////////////////////\n');


	var dead_reckoning = (function(req){
	// logic. 

	   var _ax = eval(req.body.ax*(9.8) / 2);
	   var _ay = eval(req.body.ay*(9.8));
	   var _az = eval(req.body.az*9.8);
 	   var _gx = req.body.gx;
	   var _gy = req.body.gy;
	   var _gz = req.body.gz;
  	   var _mx = req.body.mx;
	   var _my = req.body.my;
	   var _mz = req.body.mz;
	   var dist_from_beacon = req.body.dist;

	   if(max_ax < Math.abs(_ax)){
		max_ax = Math.abs(_ax);
	   }
	   if(max_ay < Math.abs(_ay)){
		max_ay = Math.abs(_ay);
	   }

	  	 
	   var scal_acc = Math.sqrt(_ax*_ax + _ay*_ay);
	  // scal_acc = scal_acc.toFixed(4);

	   var scal_velo = integral(scal_acc, 0, 1);
	   //scal_velo = scal_velo.toFixed(4);

	   var scal_dist = integral(scal_velo, 0, 1);
	   //scal_dist = scal_dist.toFixed(4);
	   
	   var _angle = Math.atan(_ay/_ax);
	   var _angle2 = _gz;
	   var mult_dist_angle_x = scal_dist * Math.sin(_angle);
	   var mult_dist_angle_y = scal_dist * Math.cos(_angle);
	   
	   // testing position X, Y whether it is correct calculate
	   // case 1. using accel sensor value to calculate position X,Y
	   // var posX = prev_X + scal_acc * Math.sin(_angle2);
	   // var posY = prev_Y + scal_acc * Math.cos(_angle2);

	   // case 2.
	   // var posX = prev_X + integral(mult_dist_angle_x, 0, 1);
	   // var posY = prev_Y + integral(mult_dist_angle_y, 0, 1);

	   // case 3. using beacon sensor dist value to calculate position X,Y
	   var posX = dist_from_beacon * Math.cos(_angle2);
	   var posY = dist_from_beacon * Math.sin(_angle2);
	   
	  // res.send('<div id="res"> Testing Page </div>'); 
	   console.log('###################################################');
	   console.log('ax, ay, az is : ' , _ax, _ay, _az);
	   console.log('gx, gy, gz is : ' , _gx, _gy, _gz);
	   console.log('scal_acc is : ', scal_acc);
	  // console.log('scal_velo is : ', scal_velo);
	  // console.log('scal_dist is : ', scal_dist);
	   console.log('angle is : ', _angle);
	   console.log('angle2 is : ', _angle2);
	   console.log('\nposX is : ', posX);
	   console.log('posY is : ', posY);
	   console.log('dist is : ', dist_from_beacon);
	   console.log('\nprev_X is : ', prev_X);
	   console.log('prev_Y is : ', prev_Y);
	   console.log('\nMax_ax is : ', max_ax);
	   console.log('Max_ay is : ', max_ay);
 	   console.log('\n');
 	   console.log('###################################################');	   	  
	   prev_X = posX;
	   prev_Y = posY;
	
	   // saving the posX, posY when we can reuse the value
	   global_x = posX;
	   global_x = Math.abs(global_x.toFixed(4)*40);

	   global_y = posY;
	   global_y = Math.abs(global_y.toFixed(4)*40);
	 
	   global_angle = Math.abs(_gz);
   	   global_dist = dist_from_beacon;
	})(req);	
	res.send('done');
	}
});

app.get('/', function(req, res, next){
	var timezone = new Date();
	var tt = timezone.toFormat('YYYY-MM-DD HH24:MI:SS');
	//res.type('application/json');
	res.header('Access-Control-Allow-Origin', '*');
	res.header('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS');
	res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Length, X-Requested-With');
//	(req.method === 'OPTIONS') ? res.send(200) : next();
	
	res.json(200, [{'x' : global_x}, {'y' : global_y}, {'theta' : global_angle}]);
	next();
	//res.send('<h1> My Response is GG </h1>');

});


http.listen(80, function(){
	console.log('Connect 80 port!');
});
