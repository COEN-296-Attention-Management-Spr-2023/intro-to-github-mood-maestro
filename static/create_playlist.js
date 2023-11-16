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

function createMoodCheckbox(mood) {
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
    // loop though moods from data base 
        let mood = ;    // per mood from database make variable
        createMoodCheckbox(mood)
    // end loop
}

// loop though available genres and create checkboxes
function loopThroughGenres() {
    // loop though genres from data base 
        let genre = ;    // per mood from database make variable
        createMoodCheckbox(genre)
    // end loop
}

function checkMoodCheckboxes() {
    // for each
        // check if checked
        // if checked add checkedbox label to array
}

function checkGenreCheckboxes() {
    // for each
            // check if checked
            // if checked add checkedbox label to array
}

function checkOptionCheckboxes() {
    // for all check if checked
        // if one checked apply
        // if two checked tell user to only use one or do both 
    // return outcome
}

// Loop though and create all available checkboxes for Moods and Genres 
loopThroughMoods();
loopThroughGenres();

// Event Listener for Generate Playlist button
const generateButton = document.querySelector('main button');
generateButton.addEventListener('click', () =>{
    checkMoodCheckboxes();
    checkGenreCheckboxes();
    var option = checkOptionCheckboxes();
    createPlaylist(option);
    // get link to playlist and open link on another page
});