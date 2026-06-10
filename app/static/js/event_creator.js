document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('sessions-container');
    const addBtn = document.getElementById('add-session-btn');
    let sessionIndex = document.querySelectorAll('.session-group').length;

    // Функция добавления новой группы сеансов
    function addSessionGroup() {
        const newGroup = document.createElement('div');
        newGroup.className = 'session-group';
        newGroup.setAttribute('data-index', sessionIndex);
        newGroup.innerHTML = `
            <button type="button" class="remove-session" title="Удалить сеанс">✖</button>
            <div class="row">
                <div class="col-md-4 mb-2">
                    <label class="form-label">Дата и время начала *</label>
                    <input type="datetime-local" name="sessions_start[]" class="form-control" required>
                </div>
                <div class="col-md-4 mb-2">
                    <label class="form-label">Дата и время окончания</label>
                    <input type="datetime-local" name="sessions_end[]" class="form-control">
                    <small class="text-muted">Необязательно, будет рассчитано автоматически если не указано</small>
                </div>
                <div class="col-md-4 mb-2">
                    <label class="form-label">Цена (руб) *</label>
                    <input type="number" step="0.01" name="sessions_price[]" class="form-control" placeholder="500" required>
                </div>
            </div>
        `;
        container.appendChild(newGroup);
        sessionIndex++;
        
        // Добавляем обработчик удаления для новой группы
        newGroup.querySelector('.remove-session').addEventListener('click', function() {
            newGroup.remove();
        });
    }

    // Удаление существующих групп (если есть кнопки удаления)
    document.querySelectorAll('.remove-session').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.session-group').remove();
        });
    });

    // Добавляем обработчик на кнопку добавления
    if (addBtn) {
        addBtn.addEventListener('click', addSessionGroup);
    }

    // ---- Конструктор зала: живой предпросмотр ----
    const rowsInput = document.getElementById('hall-rows');
    const seatsInput = document.getElementById('hall-seats-per-row');
    const previewContainer = document.getElementById('hall-preview');
    const totalCount = document.getElementById('total-seats-count');
    const customCheckbox = document.getElementById('hall-custom');
    const uniformWrapper = document.getElementById('uniform-seats-wrapper');
    const customContainer = document.getElementById('custom-seats-container');

    function getSeatsPerRow() {
        if (customCheckbox.checked) {
            const inputs = customContainer.querySelectorAll('.custom-seats-input');
            const values = [];
            inputs.forEach(inp => {
                let v = parseInt(inp.value);
                if (isNaN(v) || v < 1) v = 1;
                values.push(v);
            });
            return values;
        }
        return null;
    }

    function generateCustomInputs() {
        const rows = parseInt(rowsInput.value) || 1;
        const currentInputs = customContainer.querySelectorAll('.custom-seats-input');
        const currentValues = [];
        currentInputs.forEach(inp => currentValues.push(inp.value));

        let html = '<div class="custom-seats-grid">';
        for (let row = 1; row <= rows; row++) {
            const val = currentValues[row - 1] || 10;
            html += '<div class="custom-seats-row">';
            html += `<label class="custom-seats-label">Ряд ${row}</label>`;
            html += `<input type="number" name="custom_seats[]" class="form-control custom-seats-input" value="${val}" min="1" required>`;
            html += '<span class="custom-seats-unit">мест</span>';
            html += '</div>';
        }
        html += '</div>';
        customContainer.innerHTML = html;

        customContainer.querySelectorAll('.custom-seats-input').forEach(inp => {
            inp.addEventListener('input', renderHallPreview);
        });
    }

    function renderHallPreview() {
        const rows = parseInt(rowsInput.value) || 1;
        const perRow = getSeatsPerRow();
        let totalSeats = 0;

        let html = '<div class="hall-preview-stage">🎭 СЦЕНА</div>';
        html += '<table class="seat-map-table">';

        for (let row = 1; row <= rows; row++) {
            const seatsThisRow = perRow ? (perRow[row - 1] || 1) : (parseInt(seatsInput.value) || 1);
            totalSeats += seatsThisRow;
            const isVip = row <= 2;
            const seatClass = isVip ? 'vip' : '';
            html += '<tr>';
            html += `<td class="row-label-cell">Ряд ${row}</td>`;
            for (let seat = 1; seat <= seatsThisRow; seat++) {
                html += `<td><span class="seat-label ${seatClass}">${seat}</span></td>`;
            }
            html += '</tr>';
        }

        html += '</table>';
        previewContainer.innerHTML = html;
        totalCount.textContent = totalSeats;
    }

    function toggleCustomMode() {
        if (customCheckbox.checked) {
            uniformWrapper.style.display = 'none';
            customContainer.style.display = '';
            generateCustomInputs();
        } else {
            uniformWrapper.style.display = '';
            customContainer.style.display = 'none';
        }
        renderHallPreview();
    }

    if (rowsInput && seatsInput && previewContainer) {
        rowsInput.addEventListener('input', function() {
            if (customCheckbox.checked) generateCustomInputs();
            renderHallPreview();
        });
        seatsInput.addEventListener('input', renderHallPreview);
        if (customCheckbox) customCheckbox.addEventListener('change', toggleCustomMode);
        renderHallPreview();
    }
});