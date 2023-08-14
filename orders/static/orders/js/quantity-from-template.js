// Скрипт для заповнення значень стовпця ordQuantity в таблиці значеннями зі стовпця preQantity

$(document).ready(function() {
  $("#quantity-from-template").on("click", function() {
    $("tbody tr").each(function() {
      var preQuantityField = $(this).find("td:eq(5)").find("input[readonly]");

      if (preQuantityField.length > 0) {
        var preQuantityText = preQuantityField.attr("value");

        if (preQuantityText && preQuantityText.trim() !== "") {
          var preQuantity = parseInt(preQuantityText);

          if (!isNaN(preQuantity)) {
            console.log("Pre quantity:", preQuantity);
            console.log("Pre quantity type:", typeof preQuantity);
            $(this).find("td:eq(10) input").val(preQuantity);
            $(this).find("td:eq(10) input").trigger("change");
          }
        }
      }
    });
  });
});