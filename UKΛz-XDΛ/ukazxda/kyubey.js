setTimeout(function() {
document.getElementById("kyubey").classList.add("animated");
document.getElementById("kyubey").classList.add("fadeOut");
setTimeout(function() {
document.getElementById("kyubey").classList.remove("animated");
document.getElementById("kyubey").classList.remove("fadeOut");
document.getElementById("kyubey").style.display = "none";
}, 500);
}, 500);
var strings = ["Developer","Exynos 7870","アニメです"];
$("#_Bio").typed({
strings: strings,
typeSpeed: 10,
backDelay: 3000,
startDelay: 0,
loop: true,
loopCount: false
});
