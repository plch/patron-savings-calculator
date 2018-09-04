# patron-savings-calculator
an app designed to work with the iii discovery layer, encore to display how much the patron has "saved" by borrowing from the library

Example:


REST-API GET response:
---
```bash
$ curl --insecure https://ilsweb.plch.net:5000/2198439
{
    "min_date_epoch": 1534957500,
    "count_titles": 10,
    "patron_record_num": 2198439,
    "total_savings": 175.41
}
```

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
