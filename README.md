# patron-savings-calculator
an app designed to work with the iii discovery layer, encore to display how much the patron has "saved" by borrowing from the library

Examples:
---

*REST-API GET responses:*

*application/json data object endpoint:*
```bash
$ curl --insecure -v https://ilsweb.plch.net:5000/get/patron_savings/2198439
...
> GET /get/patron_savings/2198439 HTTP/1.1
> Host: ilsweb.plch.net:5000
> User-Agent: curl/7.52.1
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: application/json
< Content-Length: 118
< Access-Control-Allow-Origin: *
< Server: Werkzeug/0.14.1 Python/3.5.3
< Date: Mon, 10 Sep 2018 11:51:02 GMT
< 
{
  "count_titles": 11, 
  "min_date_epoch": 1534957500, 
  "patron_record_num": 2198439, 
  "total_savings": 190.4
}
```

*image/png data endpoint:*
```
$ curl --insecure -v -o /tmp/img.png https://ilsweb.plch.net:5000/get/patron_savings/img/2198439
...
> GET /get/patron_savings/img/2198439 HTTP/1.1
> Host: ilsweb.plch.net:5000
> User-Agent: curl/7.52.1
> Accept: */*
> 
{ [5 bytes data]
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
{ [5 bytes data]
< Content-Length: 6842
< Content-Type: image/png
< Last-Modified: Mon, 10 Sep 2018 11:17:23 GMT
< Cache-Control: public, max-age=43200
< Expires: Mon, 10 Sep 2018 23:17:23 GMT
< ETag: "1536578243.2968514-6842-2788433338"
< Access-Control-Allow-Origin: *
< Server: Werkzeug/0.14.1 Python/3.5.3
< Date: Mon, 10 Sep 2018 11:17:23 GMT
<

$ feh /tmp/img.png
```
![Example](https://raw.githubusercontent.com/plch/patron-savings-calculator/master/docs/feh_screenshot.png)


After fetching the REST-API GET response from the endpoint, and parsing JSON response via JavaScript:
---

![Example](https://raw.githubusercontent.com/plch/patron-savings-calculator/master/docs/encore_screenshot.png)

We can test this from encore by applying this script to the console at the "my account" page:
```javascript
var plch_script = document.createElement('script');
plch_script.type = 'application/javascript';
plch_script.src = 'https://ilsweb.plch.net:5000/js/get_patron_savings.js';
document.body.appendChild(plch_script);
```
