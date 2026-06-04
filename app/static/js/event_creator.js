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
});