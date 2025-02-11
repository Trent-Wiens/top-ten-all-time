document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded."); // Debugging log

    fetch("albums.json")
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(albums => {
            console.log("Albums loaded:", albums); // Debugging log

            let container = document.getElementById("albumContainer");
            if (!container) {
                console.error("Error: #albumContainer not found.");
                return;
            }

            container.innerHTML = ""; // Clear previous content

            albums.forEach(album => {
                // Ensure required keys exist
                if (!album["Album Name"] || !album["Artist"] || !album["Cover URL"] ||
                    !album["Spotify Link"] || !album["Apple Music Link"]) {
                    console.warn("Skipping invalid album:", album);
                    return;
                }

                let card = document.createElement("div");
                card.className = "album-card";

                let inner = document.createElement("div");
                inner.className = "album-inner";

                let front = document.createElement("div");
                front.className = "album-front";
                front.innerHTML = `<img src="${album['Cover URL']}" alt="Album Cover">`;

                let back = document.createElement("div");
                back.className = "album-back";

                // Album text and icons
                back.innerHTML = `
                    <div class="album-text">
                        <h3>${album['Album Name']}</h3>
                        <p>${album['Artist']}</p>
                    </div>
                    <div class="music-links">
                        <a href="${album['Spotify Link']}" target="_blank">
                            <img src="img/Spotify.png" alt="Spotify" class="music-icon">
                        </a>
                        <a href="${album['Apple Music Link']}" target="_blank">
                            <img src="img/AppleMusic.svg" alt="Apple Music" class="music-icon">
                        </a>
                    </div>
                `;

                // Append front and back to the inner container
                inner.appendChild(front);
                inner.appendChild(back);
                card.appendChild(inner);

                // Add flip functionality
                card.addEventListener("click", function () {
                    card.classList.toggle("flipped");
                });

                container.appendChild(card);
            });

            console.log("Album cards added.");
        })
        .catch(error => console.error("Error loading albums:", error));
});
