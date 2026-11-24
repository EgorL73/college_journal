document.getElementById('burger')?.addEventListener('click', () => {
    document.getElementById('nav').classList.toggle('open');
});

// Валидация формы добавления оценки
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.form');
    if (form) {
        form.addEventListener('submit', (e) => {
            const value = form.querySelector('#id_value');
            const student = form.querySelector('#id_student');
            
            let hasError = false;
            
            // Проверка оценки (должна быть от 2 до 5)
            if (value && (value.value < 2 || value.value > 5 || value.value === '')) {
                alert('Оценка должна быть от 2 до 5!');
                hasError = true;
            }
            
            // Проверка студента
            if (student && student.value === '') {
                alert('Выберите студента!');
                hasError = true;
            }

            if (hasError) {
                e.preventDefault(); // Останавливаем отправку
            }
        });
    }
});

// Живой поиск через fetch
const searchInput = document.getElementById('search-input');
const fetchResults = document.getElementById('fetch-results');

if (searchInput) {
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length < 2) {
            fetchResults.innerHTML = '';
            return;
        }

        fetchResults.innerHTML = '⏳ Загрузка...';

        fetch(`/api/students/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.students.length === 0) {
                    fetchResults.innerHTML = 'Ничего не найдено (fetch)';
                } else {
                    fetchResults.innerHTML = 'Найдено через API: ' + data.students.map(s => `<a href="${s.url}">${s.name}</a>`).join(', ');
                }
            })
            .catch(error => {
                fetchResults.innerHTML = 'Ошибка загрузки';
                console.error(error);
            });
    });
}