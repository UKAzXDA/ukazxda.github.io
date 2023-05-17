document.addEventListener('DOMContentLoaded', function() {
  const timerEl = document.querySelector('.timer');
  const startBtn = document.getElementById('start-btn');
  const stopBtn = document.getElementById('stop-btn');
  const reasonInput = document.getElementById('reason');
  const reportTable = document.getElementById('report').getElementsByTagName('tbody')[0];
  const totalTimeEl = document.getElementById('total-time');

  let intervalId;
  let startTime;
  let totalMinutes = 0;

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

  function appendReportEntry(entry) {
    const newRow = reportTable.insertRow(0);
    newRow.innerHTML = `
      <td  class="wow">${entry.reason}</td>
      <td  class="wow">${entry.startTime}</td>
      <td  class="wow">${entry.endTime}</td>
      <td  class="wow">${entry.totalMins}</td>
      <td  class="wow"><button_delete class="delete-btn wow">X</button_delete></td>
    `;

    totalMinutes += entry.totalMins;
    totalTimeEl.textContent = totalMinutes;
    saveTableData();

    // Remover a classe 'new-table' das outras tabelas
    const existingTables = document.querySelectorAll('.new-table');
    existingTables.forEach(table => {
      table.classList.remove('new-table');
    });

    // Adicionar a classe 'new-table' à tabela mais recente
    newRow.classList.add('new-table');

    // Remover a classe 'new-table' após um tempo para remover o destaque visual
    setTimeout(() => {
      newRow.classList.remove('new-table');
    }, 5000);
  }

  function removeReportEntry(row) {
    const totalMinsCell = row.cells[3];
    const totalMins = parseInt(totalMinsCell.textContent);
    totalMinutes -= totalMins;
    totalTimeEl.textContent = totalMinutes;

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
    const totalMins = Math.floor((endTime - startTime) / 1000 / 60);
    const entry = {
      reason: reason !== '' ? reason : '00',
      startTime: new Date(startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      endTime: new Date(endTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      totalMins: totalMins
    };
    appendReportEntry(entry);
    timerEl.textContent = '00:00:00';
    startBtn.disabled = false;
    reasonInput.disabled = false;
    stopBtn.disabled = true;
    reasonInput.value = '';
  }

  function loadTableData() {
    const tableData = localStorage.getItem('tableData');
    if (tableData) {
      const parsedData = JSON.parse(tableData);
      parsedData.forEach(data => {
        appendReportEntry(data);
      });
    }
  }

  function saveTableData() {
    const tableRows = Array.from(reportTable.rows);
    const tableData = tableRows.map(row => {
      const reason = row.cells[0].textContent;
      const startTime = row.cells[1].textContent;
      const endTime = row.cells[2].textContent;
      const totalMins = parseInt(row.cells[3].textContent);
      return { reason, startTime, endTime, totalMins };
    });
    localStorage.setItem('tableData', JSON.stringify(tableData));
  }

  loadTableData();

  startBtn.addEventListener('click', startTimer);
  stopBtn.addEventListener('click', stopTimer);

  reportTable.addEventListener('click', function(e) {
    if (e.target.classList.contains('delete-btn')) {
      const row = e.target.parentNode.parentNode;
      removeReportEntry(row);
    }
  });
});
