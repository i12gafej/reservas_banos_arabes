(function($) {
    'use strict';
    $(document).ready(function() {
        var creatorTypeSelect = $('#id_creator_type');
        var creatorIdSelect = $('#id_creator_id');

        function updateCreatorOptions(selectedType) {
            if (!selectedType) {
                creatorIdSelect.html('<option value="">---------</option>');
                return;
            }

            // Hacer una petición AJAX para obtener las opciones según el tipo
            $.ajax({
                url: '/get_creators/',
                data: {
                    'creator_type': selectedType
                },
                dataType: 'json',
                success: function(data) {
                    var options = '<option value="">---------</option>';
                    $.each(data, function(index, item) {
                        options += '<option value="' + item.id + '">' + item.name + '</option>';
                    });
                    creatorIdSelect.html(options);
                }
            });
        }

        // Actualizar cuando cambie el tipo de creador
        creatorTypeSelect.change(function() {
            updateCreatorOptions($(this).val());
        });

        // Actualizar al cargar la página si hay un valor seleccionado
        if (creatorTypeSelect.val()) {
            updateCreatorOptions(creatorTypeSelect.val());
        }
    });
})(django.jQuery); 