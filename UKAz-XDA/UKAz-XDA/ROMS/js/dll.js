var devicesElement = document.getElementById("devices");
var versionsElement = document.getElementById("versions");
var romsElement = document.getElementById("roms");
var downloadElement = document.getElementById("download");
var downloadTitleElement = document.getElementById("downloadTitle");
var downloadDateElement = document.getElementById("downloadDate");

var DivTxt = new Array()
DivTxt[0] = ""
DivTxt[1] = ""
DivTxt[2] = ""

var devices = {

"LIMPO-11": {
 	"Galaxy J7 Prime G610X": {
 		"B5-A4 Data:31-12-2020": {
 			"url": "https://drive.google.com/u/0/uc?id=19OYIUB0FRYveJLjgz_RZTcoZ0ovwCoIA&export=download",
 			"date": "OneUI-v1.1 Android-9 ARM"
			},
		},
	},

"LIMPO-Q": {
 	"Galaxy J7 Prime G610X": {
 		"A1-B1 Data:16-01-2021": {
 			"url": "https://drive.google.com/u/0/uc?id=15h1zWr7USBpHyMPFjR4O7mYasyT6szfb&export=download",
 			"date": "OneUI-v2.0 Android-10 Treble"
			},
		},
	},
};

function onDeviceChanged() {
 versionsElement.options.length = 0;
  
 if (devicesElement.selectedIndex >= 0) {
  var device = devicesElement.options[devicesElement.selectedIndex].text;
 
  if (devices[device]) {
    for (var version in devices[device]) {
     var versionOption = document.createElement("option");
     versionOption.text = version;
     versionsElement.add(versionOption);
    }
  }
 }
 
 onVersionChanged();
}
 
function onVersionChanged() {
 romsElement.options.length = 0;
  
 if (devicesElement.selectedIndex >= 0 && versionsElement.selectedIndex >= 0) {
  var device = devicesElement.options[devicesElement.selectedIndex].text;
  var version = versionsElement.options[versionsElement.selectedIndex].text;
 
  if (devices[device] && devices[device][version]) {
   for (var rom in devices[device][version]) {
        var romOption = document.createElement("option");
        romOption.text = rom;
        romsElement.add(romOption);
	document.getElementById('textDiv').innerHTML = DivTxt[versionsElement.selectedIndex];
   }
  }
 }
 
 onRomChanged();
}
 
function onRomChanged() { 
 if (devicesElement.selectedIndex >= 0 && versionsElement.selectedIndex >= 0 && romsElement.selectedIndex >= 0) {
   var device = devicesElement.options[devicesElement.selectedIndex].text;
   var version = versionsElement.options[versionsElement.selectedIndex].text;
   var rom = romsElement.options[romsElement.selectedIndex].text;
 
   if (devices[device] && devices[device][version] && devices[device][version][rom]) {
    var download = devices[device][version][rom];
   
    downloadElement.style.display = "block";
    downloadDateElement.innerText = download.date;
    downloadChangelogElement.innerHTML = download.changelog;
    onCollapseSizeChanged();
    return;
   }
 }
 
 downloadElement.style.display = "none";
}

function visitPage(){
 if (devicesElement.selectedIndex >= 0 && versionsElement.selectedIndex >= 0 && romsElement.selectedIndex >= 0) {
   var device = devicesElement.options[devicesElement.selectedIndex].text;
   var version = versionsElement.options[versionsElement.selectedIndex].text;
   var rom = romsElement.options[romsElement.selectedIndex].text;
 
   if (devices[device] && devices[device][version] && devices[device][version][rom]) {
    var download = devices[device][version][rom];
    window.location = download.url;
    return;
   }
 }
}

for (var device in devices) {
  var deviceOption = document.createElement("option");
  deviceOption.text = device;
  devicesElement.add(deviceOption);
}

devicesElement.addEventListener("change", onDeviceChanged);
versionsElement.addEventListener("change", onVersionChanged);
romsElement.addEventListener("change", onRomChanged);
 
onDeviceChanged();
