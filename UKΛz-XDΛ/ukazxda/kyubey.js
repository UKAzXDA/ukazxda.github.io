setTimeout(function() {
document.getElementById("kyubey").classList.add("animated");
document.getElementById("kyubey").classList.add("fadeOut");
setTimeout(function() {
document.getElementById("kyubey").classList.remove("animated");
document.getElementById("kyubey").classList.remove("fadeOut");
document.getElementById("kyubey").style.display = "none";
}, 500);
}, 500);
var strings = ["Exynos 7870<BR>Developer","17 y.o. self-taught<BR>my G610M device"];
$("#_Bio").typed({
strings: strings,
typeSpeed: 10,
backDelay: 3000,
startDelay: 0,
loop: true,
loopCount: false
});
