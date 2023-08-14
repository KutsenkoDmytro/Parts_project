$(document).ready(function () {
    // Обробник зміни значення поля stock
    $('#id_stock').change(function () {
        var stockId = $(this).val(); // Отримуємо обране значення stock
        var companyId = $('#id_company').val(); // Отримуємо поточне значення company

        // Перевіряємо, що ідентифікатори stock і company заповнені
        if (stockId && companyId) {
            $.ajax({
                url: '/orders/get_signatory_of_documents_options/', // URL для отримання списку опцій для поля signatory_of_documents
                data: {
                    'stock': stockId, // Передаємо обране значення stock
                    'company_id': companyId // Передаємо поточне значення company
                },
                dataType: 'json',
                success: function (data) {
                    // Очищуємо поточні опції поля signatory_of_documents
                    $('#id_signatory_of_documents').empty();

                    // Додаємо отримані опції до поля signatory_of_documents
                    $.each(data.signatory_of_documents_options, function (key, value) {
                        $('#id_signatory_of_documents').append($('<option>').text(value).attr('value', key));
                    });
                }
            });
        } else {
            // Якщо stock або company не обрані, очищуємо поле signatory_of_documents
            $('#id_signatory_of_documents').empty();
        }
    });

    // Обробник зміни значення поля company
    $('#id_company').change(function () {
        // Очищуємо поля stock, signatory_of_documents, edrpou_code та VIN_code
        $('#id_VIN_code').empty();
        $('#id_edrpou_code').val(null);
        $('#id_stock').empty();
        $('#id_signatory_of_documents').empty();
        $('#id_VIN_code').empty();

        var companyId = $(this).val(); // Отримуємо обране значення company
        if (companyId) {
            $.ajax({
                url: '/orders/get_stock_options/', // URL для отримання списку опцій для поля stock
                data: {
                    'company_id': companyId // Передаємо обране значення company
                },
                dataType: 'json',
                success: function (data) {
                    // Очищуємо поточні опції поля stock та VIN_code
                    $('#id_stock').empty();
                    $('#id_VIN_code').empty();

                    // Додаємо порожні опції для полів company, stock, signatory_of_documents, VIN_code
                    $('#id_stock').append($('<option>').text('---------').attr('value', ''));
                    $('#id_signatory_of_documents').append($('<option>').text('---------').attr('value', ''));
                    $('#id_VIN_code').append($('<option>').text('---------').attr('value', ''));

                    // Додаємо отримані опції до поля VIN_code
                    $.each(data.technique_options, function (key, value) {
                        $('#id_VIN_code').append($('<option>').text(value).attr('value', key));
                    });

                    // Додаємо отримані опції до поля stock
                    $.each(data.stock_options, function (key, value) {
                        $('#id_stock').append($('<option>').text(value).attr('value', key));
                    });

                    if (data.edrpou_code) {
                        // Обробка успішної відповіді від сервера
                        $('#id_edrpou_code').val(data.edrpou_code);
                    }
                    // Симулюємо подію зміни поля stock, щоб оновити поле signatory_of_documents
                    $('#id_stock').change();
                }
            });
        }
    });

    // Обробник зміни значення поля template
    $('#id_template').change(function () {
        // Очищуємо поля company, stock, signatory_of_documents
        $('#id_company').empty();
        $('#id_stock').empty();
        $('#id_signatory_of_documents').empty();
        $('#id_address').val('');
        $('#id_edrpou_code').val(null);
        $('#id_VIN_code').empty();

        var templateId = $(this).val(); // Отримуємо обране значення template
        if (templateId) {
            $.ajax({
                url: '/orders/get_template_order_header_options/', // URL для отримання списку опцій
                data: {
                    'template_id': templateId // Передаємо обране значення template
                },
                dataType: 'json',
                success: function (data) {
                    // Очищуємо поточні опції полів company, stock, signatory_of_documents
                    $('#id_company').empty();
                    $('#id_stock').empty();
                    $('#id_signatory_of_documents').empty();
                    $('#id_address').val('');
                    $('#id_VIN_code').empty();

                    $('#id_VIN_code').append($('<option>').text('---------').attr('value', ''));

                    // Додаємо отримані опції до поля company
                    $.each(data.company_options, function (key, value) {
                        $('#id_company').append($('<option>').text(value).attr('value', key));
                    });
                    $.each(data.stock_options, function (key, value) {
                        $('#id_stock').append($('<option>').text(value).attr('value', key));
                    });
                    $.each(data.signatory_of_documents_options, function (key, value) {
                        $('#id_signatory_of_documents').append($('<option>').text(value).attr('value', key));
                    });
                    // Додаємо отримані опції до поля VIN_code
                    $.each(data.technique_options, function (key, value) {
                        $('#id_VIN_code').append($('<option>').text(value).attr('value', key));
                    });

                    if (data.address) {
                        // Обробка успішної відповіді від сервера
                        $('#id_address').val(data.address);
                    }
                }
            });
        } else {
            // Якщо поле id_template не обране, виконати інший ajax запит
            $.ajax({
                url: '/orders/get_all_order_header_options/', // Правильний URL для іншого ajax запиту
                data: {},
                dataType: 'json', // Вкажіть тип даних, очікуваних у відповіді (у цьому випадку JSON)
                success: function (data) {
                    // Очищуємо поточні опції полів company, stock, signatory_of_documents
                    $('#id_company').empty();
                    $('#id_stock').empty();
                    $('#id_signatory_of_documents').empty();
                    $('#id_address').val('');
                    $('#id_edrpou_code').val(null);
                    $('#id_VIN_code').empty();

                    // Додаємо порожні опції для полів company, stock, signatory_of_documents, VIN_code
                    $('#id_company').append($('<option>').text('---------').attr('value', ''));
                    $('#id_stock').append($('<option>').text('---------').attr('value', ''));
                    $('#id_signatory_of_documents').append($('<option>').text('---------').attr('value', ''));
                    $('#id_VIN_code').append($('<option>').text('---------').attr('value', ''));

                    // Додаємо отримані опції до полів company, stock, signatory_of_documents_options, VIN_code
                    $.each(data.company_options, function (key, value) {
                        $('#id_company').append($('<option>').text(value).attr('value', key));
                    });
                    $.each(data.stock_options, function (key, value) {
                        $('#id_stock').append($('<option>').text(value).attr('value', key));
                    });
                    $.each(data.signatory_of_documents_options, function (key, value) {
                        $('#id_signatory_of_documents').append($('<option>').text(value).attr('value', key));
                    });
                    $.each(data.technique_options, function (key, value) {
                        $('#id_VIN_code').append($('<option>').text(value).attr('value', key));
                    });
                }
            });
        }
    });
});