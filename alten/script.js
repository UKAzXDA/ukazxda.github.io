// Seleciona os elementos HTML relevantes
const timerEl = document.querySelector('.timer');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const reasonInput = document.getElementById('reason');
const reportTable = document.getElementById('report').getElementsByTagName('tbody')[0];

let intervalId; // Variável para armazenar o ID do intervalo
let startTime; // Variável para armazenar a hora de início

// Converte um número de segundos para uma string formatada como 'HH:MM:SS'
function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor(seconds / 60) % 60;
  const secs = seconds % 60;
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Atualiza o elemento do temporizador com o tempo decorrido
function updateTimer() {
  const elapsedSecs = Math.floor((Date.now() - startTime) / 1000);
  timerEl.textContent = formatTime(elapsedSecs);
}

// Cria uma nova linha na tabela de relatórios com os dados fornecidos e adiciona o botão de remoção
function addReportEntry(reason, startTime, endTime) {
  const totalMins = Math.floor((endTime - startTime) / 1000 / 60);
  const newRow = reportTable.insertRow();
  const reasonCell = newRow.insertCell();
  const startTimeCell = newRow.insertCell();
  const endTimeCell = newRow.insertCell();
  const totalMinsCell = newRow.insertCell();
  const removeCell = newRow.insertCell();
  reasonCell.textContent = reason !== '' ? reason : '00';
  startTimeCell.textContent = new Date(startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  endTimeCell.textContent = new Date(endTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  totalMinsCell.textContent = totalMins;

  const removeButton = document.createElement('button_delete');
  removeButton.textContent = 'X';
  removeButton.addEventListener('click', function() {
    removeReportEntry(newRow);
  });
  removeCell.appendChild(removeButton);
}

// Função para remover uma linha da tabela de relatórios
function removeReportEntry(row) {
  row.remove();
}

// Inicia a contagem regressiva e atualiza o temporizador a cada segundo
function startTimer() {
  const reason = reasonInput.value;
  startTime = Date.now();
  updateTimer();
  intervalId = setInterval(updateTimer, 1000);
  startBtn.disabled = true;
  reasonInput.disabled = true;
  stopBtn.disabled = false;
}

// Pausa a contagem regressiva e adiciona uma entrada à tabela de relatórios
function stopTimer() {
  clearInterval(intervalId);
  const reason = reasonInput.value;
  const endTime = Date.now();
  addReportEntry(reason, startTime, endTime);
  timerEl.textContent = '00:00:00';
  startBtn.disabled = false;
  reasonInput.disabled = false;
  stopBtn.disabled = true;
  reasonInput.value = '';
}

// Associa os manipuladores de eventos aos botões relevantes
startBtn.addEventListener('click', startTimer);
stopBtn.addEventListener('click', stopTimer);
