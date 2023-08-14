// Функція для обробки відправки форми
    function handleSubmit(event) {
        // Перевіряємо, чи є спрацьовувальний елемент кнопкою
        if (event.submitter && event.submitter.tagName.toLowerCase() === 'button') {
            // Дозволяємо відправку форми для кнопок
            return true;
        } else {
            // Блокуємо відправку форми для не-кнопок
            event.preventDefault();
            return false;
        }
    }

    // Додаємо обробник події до форми, щоб викликати функцію handleSubmit під час відправки форми
    document.querySelector('form').addEventListener('submit', handleSubmit);

    // Додаємо обробник події для полів форми для перевірки натискання клавіші Enter
    const formFields = document.querySelectorAll('form input, form select, form textarea');
    formFields.forEach(field => {
        field.addEventListener('keydown', event => {
            if (event.key === 'Enter') {
                event.preventDefault();
            }
        });
    });