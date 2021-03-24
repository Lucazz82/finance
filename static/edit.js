// $('#edit').click(function(){
    
// })

function edit(button){
    console.log(button)
    row = $(button).parent().siblings()
    
    for (let i = 0; i < row.length; i++) {
        if (i == 0) {
            continue;
        }

        if (i == 1) {
            let value = row[i].innerHTML
            row[i].innerHTML = '<input type="text" class="form-control" value="' + value + '">'
        }

        if (i == 2) {
            let value = row[i].innerHTML
            row[i].innerHTML = '<input type="number" class="form-control" value="' + value + '">' 
        }

        if (i == 5) {
            continue;
        }

        
    
        console.log(row[i].innerHTML)
    }
}