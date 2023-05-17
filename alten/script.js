document.addEventListener('DOMContentLoaded', function() {
  const timerEl = document.querySelector('.timer');
  const startBtn = document.getElementById('start-btn');
  const stopBtn = document.getElementById('stop-btn');
  const reasonInput = document.getElementById('reason');
  const reportTable = document.getElementById('report').getElementsByTagName('tbody')[0];

  let intervalId;
  let startTime;
  let reportData = [];

  function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor(seconds / 60) % 60;
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  function updateTimer() {
    const elapsedSecs = Math.floor((Date.now() - startTime) / 1000);
    timerEl.textContent = formatTime(elapsedSecs);
  }

  function addReportEntry(reason, startTime, endTime) {
    const totalMins = Math.floor((endTime - startTime) / 1000 / 60);
    const entry = {
      reason: reason !== '' ? reason : '00',
      startTime: new Date(startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      endTime: new Date(endTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      totalMins: totalMins
    };
    reportData.push(entry);
    appendReportEntry(entry);
    saveTableData();
  }

  function appendReportEntry(entry) {
    const newRow = reportTable.insertRow();
    newRow.innerHTML = `
      <td>${entry.reason}</td>
      <td>${entry.startTime}</td>
      <td>${entry.endTime}</td>
      <td>${entry.totalMins}</td>
      <td><button_delete class="delete-btn">X</button_delete></td>
    `;

    const deleteButton = newRow.querySelector('.delete-btn');
    deleteButton.addEventListener('click', function() {
      removeReportEntry(newRow);
    });
  }

  function removeReportEntry(row) {
    const index = Array.from(reportTable.rows).indexOf(row);
    reportData.splice(index, 1);
    row.remove();
    saveTableData();
  }

  function startTimer() {
    const reason = reasonInput.value;
    startTime = Date.now();
    updateTimer();
    intervalId = setInterval(updateTimer, 1000);
    startBtn.disabled = true;
    reasonInput.disabled = true;
    stopBtn.disabled = false;
  }

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

  function loadTableData() {
    const savedData = localStorage.getItem('reportData');
    if (savedData) {
      reportData = JSON.parse(savedData);
      reportData.forEach(entry => {
        appendReportEntry(entry);
      });
    }
  }

  function saveTableData() {
    localStorage.setItem('reportData', JSON.stringify(reportData));
  }

  loadTableData();

  startBtn.addEventListener('click', startTimer);
  stopBtn.addEventListener('click', stopTimer);
});
