const container = document.getElementById('container');
const roms_osBtn = document.getElementById('roms_os-btn');
const voltarBtn = document.getElementById('voltar');

roms_osBtn.addEventListener('click', () => {
	container.classList.add("active");
});

voltarBtn.addEventListener('click', () => {
	container.classList.remove("active");
});
