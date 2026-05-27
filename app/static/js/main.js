// Проверка сложности пароля
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;
    
    if (strength <= 2) return 'weak';
    if (strength <= 4) return 'medium';
    return 'strong';
}

function updatePasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;
    
    const password = passwordInput.value;
    const strength = checkPasswordStrength(password);
    const strengthText = {
        'weak': 'Слабый',
        'medium': 'Средний',
        'strong': 'Сильный'
    };
    
    let oldHint = document.querySelector('.password-strength');
    if (oldHint) oldHint.remove();
    
    if (password.length > 0) {
        const hint = document.createElement('div');
        hint.className = `password-strength strength-${strength}`;
        hint.innerHTML = `Сложность пароля: ${strengthText[strength]}`;
        passwordInput.parentNode.appendChild(hint);
    }
}

function checkPasswordsMatch() {
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    
    if (!passwordInput || !confirmInput) return;
    
    const password = passwordInput.value;
    const confirm = confirmInput.value;
    
    let oldHint = document.querySelector('.password-match-hint');
    if (oldHint) oldHint.remove();
    
    if (confirm.length > 0 && password !== confirm) {
        const hint = document.createElement('div');
        hint.className = 'password-strength strength-weak password-match-hint';
        hint.innerHTML = '✗ Пароли не совпадают';
        confirmInput.parentNode.appendChild(hint);
        confirmInput.style.borderColor = '#dc3545';
    } else if (confirm.length > 0 && password === confirm) {
        const hint = document.createElement('div');
        hint.className = 'password-strength strength-strong password-match-hint';
        hint.innerHTML = '✓ Пароли совпадают';
        confirmInput.parentNode.appendChild(hint);
        confirmInput.style.borderColor = '#198754';
    } else {
        confirmInput.style.borderColor = '#ced4da';
    }
}

// Автоматическое скрытие flash-сообщений через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация проверки пароля на странице регистрации
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            updatePasswordStrength();
            checkPasswordsMatch();
        });
    }
    
    if (confirmInput) {
        confirmInput.addEventListener('input', checkPasswordsMatch);
    }
    
    // Авто-скрытие alert'ов
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Подтверждение отмены бронирования
    const cancelButtons = document.querySelectorAll('.cancel-booking');
    cancelButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            if (!confirm('Вы уверены, что хотите отменить бронирование?')) {
                e.preventDefault();
            }
        });
    });
    
    // Фильтр мероприятий без перезагрузки (опционально)
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', () => {
            window.location.href = `/events?category=${categoryFilter.value}`;
        });
    }
});

// Форматирование телефона (опционально)
function formatPhone(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 11) value = value.slice(0, 11);
    
    if (value.length === 11) {
        value = value.replace(/(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})/, '+$1 ($2) $3-$4-$5');
    }
    input.value = value;
}

// Для страницы выбора мест - выбираем все места в ряду
function selectAllInRow(rowId) {
    const checkboxes = document.querySelectorAll(`.row-${rowId} input[type="checkbox"]`);
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => cb.checked = !allChecked);
}