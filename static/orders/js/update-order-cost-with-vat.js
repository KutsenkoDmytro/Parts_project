
$(document).ready(function() {
    console.log("Скрипт ініціалізовано");
    var vatRate = 1.2; // Значення ставки ПДВ за замовчуванням

    $("#id_{{ form.prefix }}-ord_quantity").on("change", function() {
        var quantity = parseInt($(this).val());
        var price = parseFloat("{{ form.price.value }}");

        var cost = quantity * price;
        var costWithVat = cost * vatRate;

        // Оновлення значень у таблиці
        $(this).closest("tr").find(".ord_cost").text(cost.toFixed(2));
        $(this).closest("tr").find(".ord_cost_with_vat").text(costWithVat.toFixed(2));

        updateTotal();
    });

    function updateTotal() {
         // Оновлюємо значення total і total_with_VAT
        var total = 0;
        var total_with_VAT = 0;

        // Проходимо по всім рядкам таблиці та сумуємо значення ord_cost і ord_cost_with_vat
        $("tbody tr").each(function() {
            var ord_cost = parseFloat($(this).find(".ord_cost").text());
            var ord_cost_with_vat = parseFloat($(this).find(".ord_cost_with_vat").text());

            if (!isNaN(ord_cost)) {
                total += ord_cost;
            }

            if (!isNaN(ord_cost_with_vat)) {
                total_with_VAT += ord_cost_with_vat;
            }
        });

        // Оновлюємо значення на сторінці
        $("#total").text(total.toFixed(2));
        $("#total_with_vat").text(total_with_VAT.toFixed(2));
    }

    // Викликаємо функцію оновитиВсьогоЗагальнуСуму() після завантаження сторінки та після зміни кількості
    $("#id_{{ form.prefix }}-ord_quantity").on("change", updateTotal);
});