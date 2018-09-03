// this matches 6 or more numbers in the string ... is more simple, but less accurate
var patron_num_re = /[0-9]{6,}/;
// or we can use this one to match any lenght of number as long as they come after a '/' (negative look around) and before a '/newpin' value (positive look around)
// more complex, and may work better, depending on the situation.
// var patron_num_re = (?<=\/)([0-9]{1,})(?=\/newpin)
patron_num_re.exec(document.getElementById('modPinPopupWindowLinkComponent').getAttribute('onclick'))[0];
