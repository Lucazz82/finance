$('#instalments').change(function(){
    if($(this).val() == 'yes') {

        $('#instalments-label').removeClass('d-none');
        $('#instalments-number').removeClass('d-none');

    } else {

        $('#instalments-label').addClass('d-none');
        $('#instalments-number').addClass('d-none');

    }
});
