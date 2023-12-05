$(document).ready(function(){
    function updateSongs() {
        $.ajax({
            url: '/get_updated_songs',
            type: 'GET',
            success: function(response){
                response.forEach(song => {
                    let songElement = $(`#song-${song.id}`);
                    songElement.find('.genres').text(`Genres: ${song.genres ? song.genres.join(', ') : 'N/A'}`);
                    songElement.find('.moods').text(`Mood: ${song.moods || 'N/A'}`);
                    songElement.find('.danceability').text(`Danceability: ${song.features.danceability || 'N/A'}`);
                    songElement.find('.energy').text(`Energy: ${song.features.energy || 'N/A'}`);
                    songElement.find('.key').text(`Key: ${song.features.key || 'N/A'}`);
                    songElement.find('.loudness').text(`Loudness: ${song.features.loudness || 'N/A'}`);
                    songElement.find('.speechiness').text(`Speechiness: ${song.features.speechiness || 'N/A'}`);
                    songElement.find('.tempo').text(`Tempo: ${song.features.tempo || 'N/A'}`);
                    songElement.find('.valence').text(`Valence: ${song.features.valence || 'N/A'}`);

                });
            },
            error: function(){
                console.log('Error fetching updated songs');
            }
        });
    }

    // Set interval for updating songs every 3 seconds
    setInterval(updateSongs, 3000);
});