# patron-savings-calculator
an app designed to work with the iii discovery layer, encore to display how much the patron has "saved" by borrowing from the library

Example:

We can test this from encore by applying this script to the console at the "my account" page:
```javascript
var plch_script = document.createElement('script');
plch_script.type = 'application/javascript';
plch_script.src = 'https://ilsweb.plch.net:5000/js/get_patron_savings.js';
document.body.appendChild(plch_script);
```

REST-API GET response:
---

![Example](https://raw.githubusercontent.com/plch/patron-savings-calculator/master/docs/Screenshot-2018-09-04.png)

After fetching the REST-API GET response from the endpoint, and parsing it via JavaScript:
---

![Example](https://raw.githubusercontent.com/plch/patron-savings-calculator/master/docs/Screenshot2018-09-04-2.png)
