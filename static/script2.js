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
    if (resp.data.title){
        $("#dictionary-results").append(`<p>${resp.data.title}</p>`)

    }else{
        $("#dictionary-results").append(`<p>${resp.data.word.definitions}</p>`)
        $("#dictionary-results").append(`<p>${resp.data.word.word}</p>`)
        $("#dictionary-results").append(`<p>${resp.data.word.grammer}</p>`)
        $("#dictionary-results").append(`<p>${resp.data.word.synonyms}</p>`)
        $("#dictionary-results").append(`<p>${resp.data.word.examples}</p>`)
        $("#dictionary-results").append(`<p>${resp.data.word.audio}</p>`)
        $("#dictionary-results").append(`<p><a class="btn btn-primary" href="/save" id=save-button>Add</a></p>`)
        $("#save-button").on('click',sendrequest);
        
    }


}

async function sendrequest(evt){
    evt.preventDefault();
    const request =await axios.post('http://127.0.0.1:5000/save', {
        "word":resp.data.word.word,
        "definitions":resp.data.word.definitions

    })
    console.log(request)

}



$("#dictionary-form").on("submit", processForm);


