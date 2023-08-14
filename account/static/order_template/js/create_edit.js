$(document).ready(function () {
    // Обробник зміни значення поля stock
    $('#id_stock').change(function () {
        var stockId = $(this).val(); // Отримуємо обране значення stock
        var userCompanyName = $('#id_user_company').val(); // Отримуємо поточне значення user_company

        // Перевіряємо, що ідентифікатори stock і user_company заповнені
        if (stockId && userCompanyName) {
            $.ajax({
                url: '/account/get_responsible_person_options/', // URL для отримання списку опцій для поля responsible_person
                data: {
                    'stock': stockId, // Передаємо обране значення stock
                    'user_company_id': userCompanyName // Передаємо поточне значення user_company
                },
                dataType: 'json',
                success: function (data) {
                    // Очищуємо поточні опції поля responsible_person
                    $('#id_responsible_person').empty();

                    // Додаємо отримані опції до поля responsible_person
                    $.each(data.responsible_person_options, function (key, value) {
                        $('#id_responsible_person').append($('<option>').text(value).attr('value', key));
                    });
                }
            });
        } else {
            // Якщо stock або user_company не обрані, очищуємо поле responsible_person
            $('#id_responsible_person').empty();
        }
    });

    // Обробник зміни значення поля user_company
    $('#id_user_company').change(function () {
        // Очищуємо поля stock і responsible_person
        $('#id_stock').empty();
        $('#id_responsible_person').empty();

        var userCompanyName = $(this).val(); // Отримуємо обране значення user_company
        if (userCompanyName) {
            $.ajax({
                url: '/account/get_stock_options/', // URL для отримання списку опцій для поля stock
                data: {
                    'user_company_id': userCompanyName // Передаємо обране значення user_company
                },
                dataType: 'json',
                success: function (data) {
                    // Очищуємо поточні опції поля stock
                    $('#id_stock').empty();

                    // Додаємо отримані опції до поля stock
                    $.each(data.stock_options, function (key, value) {
                        $('#id_stock').append($('<option>').text(value).attr('value', key));
                    });

                    // Симулюємо подію зміни поля stock, щоб оновити поле responsible_person
                    $('#id_stock').change();
                }
            });
        }
    });
});