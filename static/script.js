async function processForm(evt) {
    evt.preventDefault();
    let word= $('#word').val()
    // console.log(word)
    const resp =await axios.post('http://127.0.0.1:5000/api/get-word', {
        word,
    })
    console.log(resp)
    handleResponse(resp)
    
    

}

function handleResponse(resp) {
    $("#dictionary-results").empty()
    $("#dictionary-results").append(`<p>${resp.data.word.definitions}</p>`)
    

}



$("#dictionary-form").on("submit", processForm);

