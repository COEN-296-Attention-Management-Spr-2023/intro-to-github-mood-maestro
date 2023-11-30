/*
    get list of genres
        loop through and create checkboxes
            <input type="checkbox" id="{genre}" name="{genre}" value="{genre}">
            <label for="{genre}">{genre}</label><br>
    get list of moods
        loop through and create checkboxes
            <input type="checkbox" id="{mood}" name="{mood}" value="{mood}">
            <label for="{mood}">{mood}</label><br>

    on button press event
        find checked checkboxes
        use those checked to generate playlist
            Options
                1. find all songs that have a single one of the genres and moods
                2. find all songs that have all the genres and moods attached
        get created playlist ID
        maybe try to link to the created playlist in spotify (if there is time)
*/

const moods = [];
const genres = [];

function createMoodCheckbox(mood) { // NEED TO STILL 
    // create checkbox element
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = mood;
    checkbox.name = "mood";
    checkbox.value = mood;
    

    // create label element and append to checkbox
    var label = document.createElement("label");
    label.htmlFor = mood;
    label.appendChild(document.createTextNode(mood));

    // append to parent
    var parent = document.getElementsByClassName("mood_list")
    parent.appendChild(checkbox);
    parent.appendChild(label);
}

function createGenreCheckbox(genre) {
    // create checkbox element
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = genre;
    checkbox.name = "genre";
    checkbox.value = genre;
    

    // create label element and append to checkbox
    var label = document.createElement("label");
    label.htmlFor = genre
    label.appendChild(document.createTextNode(genre));

    // append to parent
    var parent = document.getElementsByClassName("genre_list");
    parent.appendChild(checkbox);
    parent.appendChild(label);
}

// loop though available moods and create checkboxes
function loopThroughMoods() {
    // if no moods do nothing
    // else set ul.mood_list p.NA to have "hidden" class
    // loop though moods from data base 
    
        // let mood = ;    // per mood from database make variable
        // createMoodCheckbox(mood)
    // end loop
}

// loop though available genres and create checkboxes
function loopThroughGenres() {
    // if no moods do nothing
    // else set ul.genre_list p.NA to have "hidden" class
    // loop though genres from data base 
        // let genre = ;    // per mood from database make variable
        // createMoodCheckbox(genre)
    // end loop
}

function checkMoodCheckboxes() {
    // for each
        // check if checked
        // if checked add checkedbox label to moods[]
}

function checkGenreCheckboxes() {
    // for each
            // check if checked
            // if checked add checkedbox label to genres[]
}

// function checkOptionCheckboxes() {
//     let outcome = 0;
//     // for each see if checked
//         // if both checked tell user to use one or do both versions
//             outcome = 1;
//         // if songs with a genre/mood checked 
//             outcome = 2;
//         // if songs with all genres/mood checked
//             outcome = 3;
//     return outcome
// }

// function createPlaylist() {
//     // pass though option, moods, genres
//     // create playlist
// }

// Loop though and create all available checkboxes for Moods and Genres 
// might not be needed as we can loop in the html file
// loopThroughMoods();
// loopThroughGenres();

// Event Listener for Generate Playlist button
const generateButton = document.querySelector('main button');
generateButton.addEventListener('click', () =>{
    checkMoodCheckboxes();
    checkGenreCheckboxes();
    
    // var option = checkOptionCheckboxes();
    // if(option !== 0){
    //     createPlaylist(option, moods, genres);
    //     // get link to playlist and open link on another page
    // }
    // output need to choose an potion or no nothing
});