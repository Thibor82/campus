const container = document.getElementById("pokemons");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");

let currentUrl = "https://pokeapi.co/api/v2/pokemon?limit=12";

function loadPokemons(url) {
  if (!url) return;
  
  container.innerHTML = "<p>Cargando pokémon...</p>";

  fetch(url)
    .then(res => res.json())
    .then(data => {
      container.innerHTML = "";

      data.results.forEach(pokemon => {
        fetch(pokemon.url)
          .then(res => res.json())
          .then(pokeData => {
            const card = `
              <div class="card">
                <img src="${pokeData.sprites.front_default}" alt="${pokeData.name}">
                <p>${pokeData.name}</p>
              </div>
            `;

            container.insertAdjacentHTML("beforeend", card);
          });
      });

      prevBtn.style.display = data.previous ? "inline-block" : "none";
      nextBtn.style.display = data.next ? "inline-block" : "none";

      prevBtn.onclick = () => loadPokemons(data.previous);
      nextBtn.onclick = () => loadPokemons(data.next);
    })
    .catch(error => {
      console.error("Error cargando pokémon:", error);
      container.innerHTML = "<p>Error al cargar pokémon</p>";
    });
}

loadPokemons(currentUrl);   