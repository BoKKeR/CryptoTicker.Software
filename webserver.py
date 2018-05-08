from microWebSrv import MicroWebSrv
import btree

try:
    f = open("settings", "r+b")
except OSError:
    f = open("settings", "w+b")
    db = btree.open(f)
    db[b"display0"] = b"bitcoin"
    db[b"display1"] = b"litecoin"
    db[b"display2"] = b"bitcoin"
    db[b"display3"] = b"bitcoin"
    db.flush()

db = btree.open(f)

# ----------------------------------------------------------------------------

@MicroWebSrv.route('/')
def _httpHandlerTestGet(httpClient, httpResponse) :
	content = """\
	<!DOCTYPE html>
	<html lang=fr>
        <head>
	        <script src="https://code.jquery.com/jquery-2.1.1.min.js" type="text/javascript"></script>
			<link href="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.1/css/select2.min.css" rel="stylesheet" />
			<script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.1/js/select2.min.js"></script>
			<script type="text/javascript">

				var coins = [];


				$(document).ready(function() {
				 //   $('#btn').click(function() {
				        $.getJSON("https://api.coinmarketcap.com/v1/ticker/", function(data){
						    for (var i = 0, len = data.length; i < len; i++) {
						        console.log(data[i].id);
						        coins.push(data[i].id);
						    }
							$("#display0").select2({
							  data: coins
							});
							$("#display1").select2({
							  data: coins
							});
							$("#display2").select2({
							  data: coins
							});
							$("#display3").select2({
							  data: coins
							});	
							$('#display0').val('%s').trigger('change');
							$('#display1').val('%s').trigger('change');
							$('#display2').val('%s').trigger('change');
							$('#display3').val('%s').trigger('change');
						});
				  //  });
				});

			</script>
        	<meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>Settings</h1>
            <br />
			<form action="/" method="post" accept-charset="ISO-8859-1">
			<div>
				Display 0: <select name="display0" id="display0" style="width:150px;">
				</select>
			</div>
			<div>
				Display 1: <select name="display1" id="display1" style="width:150px;">
				</select>
			</div>
			<div>
				Display 2: <select name="display2" id="display2" style="width:150px;">
				</select>
			</div>
			<div>
				Display 3: <select name="display3" id="display3" style="width:150px;">
				</select>
			</div>
			<input type="submit" value="Save Settings">
			</form>						
		<div>
        	
    	</div>
        </body>
    </html>
	""" % (db[b"display0"].decode("utf-8"),
		   db[b"display1"].decode("utf-8"),
		   db[b"display2"].decode("utf-8"),
		   db[b"display3"].decode("utf-8"))
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

# ----------------------------------------------------------------------------

@MicroWebSrv.route('/', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
	formData  = httpClient.ReadRequestPostedFormData()
	display0 = formData["display0"]
	display1 = formData["display1"]
	display2 = formData["display2"]
	display3 = formData["display3"]

	db[b"display0"] = str.encode(display0)
	db[b"display1"] = str.encode(display1)
	db[b"display2"] = str.encode(display2)
	db[b"display3"] = str.encode(display3)
	db.flush()

	content   = """\
	<!DOCTYPE html>
	<html lang=fr>
		<head>
			<meta charset="UTF-8" />
            <title>Settings saved</title>
        </head>
        <body>
            <h1>Settings saved</h1>
            Display0 = %s<br />
            Display1 = %s<br />
            Display2 = %s<br />
            Display3 = %s<br />
        </body>
    </html>
	""" %  (MicroWebSrv.HTMLEscape(display0),
		    MicroWebSrv.HTMLEscape(display1),
		    MicroWebSrv.HTMLEscape(display2),
		    MicroWebSrv.HTMLEscape(display3))
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

# ----------------------------------------------------------------------------

srv = MicroWebSrv(webPath='www/')
srv.MaxWebSocketRecvLen     = 256
srv.WebSocketThreaded		= False
srv.Start(threaded=True)

# ----------------------------------------------------------------------------
