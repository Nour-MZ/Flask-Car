var recentSearches = JSON.parse(localStorage.getItem("recentSearches")) || [];
var recommendations = JSON.parse(localStorage.getItem("recommendStorage")) || [];

const searchinput = document.getElementById("searchInput")
const searchForm = document.getElementById("searchForm")
const autocompleteSuggestions = document.getElementById("autocompletesuggestion")

let pendingRequest = null;

async function getAutocompleteSuggestions() {
    const query = searchinput.value.trim();
    if (pendingRequest) {
        pendingRequest.abort();
      }
    if (query.length > 0) {
      try {
        const response = await fetch(`/autocomplete?query=${query}`);
        const words = await response.json();
        console.log("wrods", words)
        autocompleteSuggestions.innerHTML = '';
        words.forEach(word => {
          const suggestion = document.createElement('div');
          suggestion.textContent = word;
          autocompleteSuggestions.appendChild(suggestion);
        });
      } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Request was cancelled');
          } else {
            console.error('Error fetching suggestions:', error);
          }
      }
    } else {
      autocompleteSuggestions.innerHTML = '';
    }
  }


function updateTable(data, tableId) {
    var tableBody = document.querySelector(tableId + " tbody");
    tableBody.innerHTML = "";
    console.log(data);
    data.forEach(function (car) {
        console.log("randoom");
        var row = document.createElement("tr");
        row.innerHTML = `
    <td>${car[Object.keys(car)[0]].brand}</td>
    <td>${car[Object.keys(car)[0]].model}</td>
    <td>${car[Object.keys(car)[0]].year}</td>
    <td>${car[Object.keys(car)[0]].color}</td>
    <td>${car[Object.keys(car)[0]].size}</td>
    <td>${car[Object.keys(car)[0]].fuel}</td>
  `;
        tableBody.appendChild(row);
    });
}

async function fetchCarData(query) {
    try {
        const response = await fetch(
            `/search?query=${encodeURIComponent(query)}`
        );
        const carList = await response.json();
        console.log(carList)

        const table = document.getElementById("carList");
        tableBody = document.getElementById("CarListBody");
        tableBody.innerHTML = "";

        carList.forEach((x) => {
            var row = document.createElement("tr");
            row.innerHTML = `
      <td>${x.brand}</td>
      <td>${x.model}</td>
      <td>${x.year}</td>
      <td>${x.color}</td>
      <td>${x.size}</td>
      <td>${x.fuel}</td>
    `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching car data:", error);
    }
}

function updateSearch(searchhis) {
    document.getElementById("recentSearches").innerHTML = "";
    searchhis.forEach(function (e) {
        var li = document.createElement("li");
        li.textContent = e;
        document.getElementById("recentSearches").appendChild(li);
    });
}

updateTable(recommendations, "#recommendation")
updateSearch(recentSearches);


searchinput.addEventListener("input", getAutocompleteSuggestions)

searchForm.addEventListener("submit", (e) => {
        e.preventDefault();

        searchQuery = searchinput.value;

        recentSearches.unshift(searchQuery);
        recentSearches = recentSearches.slice(0, 10);

        updateSearch(recentSearches);
        localStorage.setItem(
            "recentSearches",
            JSON.stringify(recentSearches)
        );

        fetchCarData(searchQuery);

        axios
            .get("/recommend?items=" + recentSearches)
            .then(function (response) {
                var recommendList = response.data;

                updateTable(recommendList, "#recommendation");

                localStorage.setItem(
                    "recommendStorage",
                    JSON.stringify(recommendList)
                );
            })
            .catch(function (error) {
                console.error("Error fetching car models:", error);
            });
            searchinput.value = "";   
            autocompleteSuggestions.innerHTML = "";
    });