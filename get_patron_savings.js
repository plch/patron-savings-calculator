var plch_patron_savings_api_address = 'https://ilsweb.plch.net:5000/'
var plch_xhttp = new XMLHttpRequest();

plch_xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
       // Action to be performed when the document is read;
       plch_data = JSON.parse(this.responseText);
       console.log('got the response back... creating the node...')
       plch_create_savings_node(plch_data);
    }
};

plch_create_savings_node = function (plch_data) {
    var plch_savings_node_id = 'plch_savings_node';
    // remove any previous instances of the node (in case we've created it previously...)
    try {
        document.getElementById(plch_savings_node_id).outerHTML = '';
    }
    catch(err) {
        console.log('no existing nodes, fetching the data for the first time.');
    }

    var plch_d = new Date(0); // The 0 there is the key, which sets the date to the epoch
    plch_d.setUTCSeconds(plch_data.min_date_epoch);
    // find the parent node that we want to append to
    var savings_node_parent = document.getElementsByClassName('accountSummaryColumn')[1];
    // create the new node that will contain the display text and style
    var savings_node = document.createElement('span');
    savings_node.id = plch_savings_node_id;
    savings_node.style.color = 'green';
    var savings_node_title = document.createElement('h4');
    savings_node_title.style.paddingTop = '10px';
    savings_node_title.innerHTML = 'Approximate Savings*:';
    var savings_node_text = document.createTextNode('$' + plch_data.total_savings + ' (since ' + plch_d.toLocaleDateString('en-us') + ')' );

    savings_node.appendChild(savings_node_title);
    savings_node.appendChild(savings_node_text);

    savings_node_parent.appendChild(savings_node);
}

// only perform the value calculation if we're on the myaccount page
if (window.location.pathname === '/iii/encore/myaccount') {
    // this matches 6 or more numbers in the string ... is more simple, but less accurate
    var patron_num_re = /[0-9]{6,}/;
    // or we can use this one to match any lenght of number as long as they come after a '/' (negative look around) and before a '/newpin' value (positive look around)
    // more complex, and may work better, depending on the situation.
    // var patron_num_re = (?<=\/)([0-9]{1,})(?=\/newpin)
    var patron_record_num = patron_num_re.exec(document.getElementById('modPinPopupWindowLinkComponent').getAttribute('onclick'))[0];
    console.log('patron_record_num: ' + patron_record_num);

    // send the request
    plch_xhttp.open("GET", plch_patron_savings_api_address + patron_record_num, true);
    plch_xhttp.send();

    
}