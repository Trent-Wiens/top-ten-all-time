document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded."); // Debugging log

    fetch("albums.json")
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(albums => {
            console.log("Albums loaded:", albums); // Debugging log

            albums.sort((a,b) => b.Sum - a.Sum);

            let container = document.getElementById("albumContainer");
            if (!container) {
                console.error("Error: #albumContainer not found.");
                return;
            }

            container.innerHTML = ""; // Clear previous content

            albums.forEach(album => {
                // Ensure required keys exist
                if (!album["Album Name"] || !album["Artist"] || !album["Cover Path"] ||
                    !album["Spotify Link"] || !album["Apple Music Link"] || !album["Radar Plot"]) {
                    console.warn("Skipping invalid album:", album);
                    return;
                }

                let card = document.createElement("div");
                card.className = "album-card";

                let inner = document.createElement("div");
                inner.className = "album-inner";

                let front = document.createElement("div");
                front.className = "album-front";
                // front.innerHTML = `<img src="${album['Cover Path']}" alt="Album Cover">`;
                front.innerHTML = `<video autoplay muted loop playsinline><source src="${album['Cover Path']}" type="video/mp4"></video>`;

                let back = document.createElement("div");
                back.className = "album-back";

                // Radar plot tab
                let radarTab = document.createElement("div");
                radarTab.className = "radar-tab";
                radarTab.innerText = "Radar Plot";

                let radarPanel = document.createElement("div");
                radarPanel.className = "radar-panel";
                radarPanel.innerHTML = `<img src="${album['Radar Plot']}" alt="Radar Plot">`;

                // Toggle radar panel on tab click
                radarTab.addEventListener("click", function (event) {
                    event.stopPropagation(); // Prevent flipping when clicking the tab
                
                    if (!radarPanel.classList.contains("open")) {
                        radarPanel.classList.add("open");
                        radarTab.classList.add("open");
                    } else {
                        radarPanel.classList.remove("open");
                        radarTab.classList.remove("open");
                    }
                });

                radarPanel.addEventListener("click", function (event) {
                    event.stopPropagation(); // Prevent flipping when clicking the tab
                
                    if (!radarPanel.classList.contains("open")) {
                        radarPanel.classList.add("open");
                        radarTab.classList.add("open");
                    } else {
                        radarPanel.classList.remove("open");
                        radarTab.classList.remove("open");
                    }
                });

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

                // Append elements

                inner.appendChild(front);
                inner.appendChild(back);
                card.appendChild(inner);
                card.appendChild(radarPanel);  // ✅ Separate from album-back
                card.appendChild(radarTab);


                card.addEventListener("click", function () {
                    if (!card.classList.contains("flipping")) {
                        card.classList.add("flipping");
                
                        setTimeout(() => {
                            card.classList.toggle("flipped");
                            radarTab.classList.toggle("flipped");
                            radarPanel.classList.toggle("flipped");
                        }, 10); // Small delay before flipping starts

                        if (radarPanel.classList.contains("open")) {
                            radarPanel.classList.remove("open");
                            radarTab.classList.remove("open");
                        }
                        
                
                        setTimeout(() => {
                            card.classList.remove("flipping"); // Remove class after animation ends
                            radarPanel.style.opacity = "1"; // Show radar panel after animation
                            // radarTab.style.opacity = "1";
                        }, 600); // Adjust this time to match CSS flip animation duration
                
                        // Hide radar panel while flipping
                        radarPanel.style.opacity = "0";
                        // radarTab.style.opacity = "0";
                    }
                });

                // // Add flip functionality
                // card.addEventListener("click", function () {
                //     card.classList.toggle("flipped");
                //     radarTab.classList.toggle("flipped");
                // });

                container.appendChild(card);
            });

            console.log("Album cards added.");
        })
        .catch(error => console.error("Error loading albums:", error));
});
