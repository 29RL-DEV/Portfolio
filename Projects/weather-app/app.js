/**
 * WeatherSync - Global Weather Intelligence
 * Modern, real-time weather application with 5-day forecast
 * Built with Open-Meteo + Nominatim (both free, unlimited APIs)
 */

import {
  searchCities,
  fetchWeatherByCoords,
  getWeatherDescription,
  getWeatherIcon,
} from "./src/api.js";

import {
  addToSearchHistory,
  getTemperatureUnit,
  setTemperatureUnit,
  saveLastCity,
  getLastCity,
} from "./src/storage.js";

import {
  formatDate,
  showSpinner,
  showErrorMsg,
  hideError,
  showData,
  displaySuggestions,
  clearSuggestions,
  displayCurrentWeather,
  displayForecast,
  updateUnitDisplay,
  getSearchInput,
  setSearchInput,
  clearSearchInput,
  focusSearchInput,
} from "./src/ui.js";

// App state
let useCelsius = getTemperatureUnit();
let searchTimeout;
let searchAbortController = null;

// DOM elements
const btn = document.getElementById("searchBtn");
const input = document.getElementById("searchInput");
const switchUnitBtn = document.getElementById("toggleUnit");
const homeBtn = document.getElementById("homeBtn");
const errorCloseBtn = document.getElementById("errorCloseBtn");

/**
 * Initialize application
 */
document.addEventListener("DOMContentLoaded", () => {
  // Event listeners
  btn.addEventListener("click", handleSearch);
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSearch();
  });

  input.addEventListener("input", handleInputChange);

  switchUnitBtn.addEventListener("click", handleUnitToggle);

  if (homeBtn) {
    homeBtn.addEventListener("click", () => location.reload());
  }

  if (errorCloseBtn) {
    errorCloseBtn.addEventListener("click", hideError);
  }

  // Close suggestions when clicking outside
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search")) {
      clearSuggestions();
    }
  });

  // Nu mai încărca automat ultima căutare
  focusSearchInput();
});

/**
 * Handle search input changes (autocomplete)
 */
async function handleInputChange(e) {
  const query = e.target.value.trim();

  if (!query) {
    clearSuggestions();
    return;
  }

  // Cancel previous request if still pending
  if (searchAbortController) {
    searchAbortController.abort();
  }
  searchAbortController = new AbortController();

  clearTimeout(searchTimeout);

  // Show "Searching..." message immediately
  const suggestions = document.getElementById("suggestions");
  suggestions.innerHTML =
    '<li style="color: var(--muted); font-style: italic;">🔍 Searching...</li>';

  // Debounce: wait 300ms before API call (reduced unnecessary requests)
  searchTimeout = setTimeout(async () => {
    try {
      const cities = await searchCities(query, searchAbortController.signal);
      displaySuggestions(cities, selectCity);
    } catch (err) {
      // Don't show error if request was aborted (user typed more)
      if (err.name !== "AbortError") {
        suggestions.innerHTML =
          '<li style="color: var(--danger);">⚠️ Error loading suggestions</li>';
      }
    }
  }, 300);
}

/**
 * Handle search button click
 */
async function handleSearch() {
  const query = getSearchInput();

  if (!query) {
    showErrorMsg("Please type a city name");
    return;
  }

  clearSuggestions();
  hideError();
  showSpinner(true);

  try {
    const cities = await searchCities(query);

    if (!cities || cities.length === 0) {
      showErrorMsg("City not found. Try another search.");
      showData(false);
      return;
    }

    displaySuggestions(cities, selectCity);
  } catch (err) {
    showErrorMsg("Error: " + (err.message || "Unable to search cities"));
    showData(false);
  } finally {
    showSpinner(false);
  }
}

/**
 * Handle city selection from suggestions
 */
async function selectCity(city, displayName) {
  setSearchInput(displayName);
  hideError();
  showSpinner(true);

  try {
    // Fetch weather for selected city
    const weatherData = await fetchWeatherByCoords(city.lat, city.lon);

    // Display weather
    displayCurrentWeather(weatherData, displayName, useCelsius);
    displayForecast(weatherData, useCelsius);

    // Load map
    const temp = useCelsius
      ? Math.round(weatherData.current.temperature_2m)
      : Math.round((weatherData.current.temperature_2m * 9) / 5 + 32);
    updateWeatherMap(city.lat, city.lon, temp);

    // Show data sections
    showData(true);

    // Save doar în search history, nu și ca last city
    addToSearchHistory(displayName);
  } catch (err) {
    showErrorMsg(err.message || "Could not fetch weather data");
    showData(false);
  } finally {
    showSpinner(false);
  }
}

/**
 * Handle temperature unit toggle
 */
function handleUnitToggle() {
  useCelsius = !useCelsius;
  setTemperatureUnit(useCelsius);
  updateUnitDisplay(useCelsius);

  // Refresh current weather display with new unit
  const lastCityData = getLastCity();
  if (lastCityData) {
    showSpinner(true);
    fetchWeatherByCoords(lastCityData.lat, lastCityData.lon)
      .then((data) => {
        displayCurrentWeather(data, lastCityData.city, useCelsius);
        displayForecast(data, useCelsius);
        const temp = useCelsius
          ? Math.round(data.current.temperature_2m)
          : Math.round((data.current.temperature_2m * 9) / 5 + 32);
        updateWeatherMap(lastCityData.lat, lastCityData.lon, temp);
      })
      .catch((err) => showErrorMsg(err.message))
      .finally(() => showSpinner(false));
  }
}

/**
 * Load and display last viewed city on app start
 */
function loadLastCity() {
  // Eliminat funcția - nu mai e folosită
}

/**
 * Display Windy weather map iframe
 */
function updateWeatherMap(lat, lon, temp) {
  const mapContainer = document.getElementById("map");

  if (!mapContainer) return;

  mapContainer.innerHTML =
    '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--muted); font-style: italic;">Loading weather map...</div>';

  setTimeout(() => {
    const windyUrl = `https://embed.windy.com/embed2.html?lat=${lat}&lon=${lon}&zoom=10&level=surface&overlay=wind&product=ecmwf&message=true`;

    const iframe = document.createElement("iframe");
    iframe.src = windyUrl;
    iframe.style.width = "100%";
    iframe.style.height = "100%";
    iframe.style.border = "none";
    iframe.style.borderRadius = "10px";
    iframe.frameBorder = "0";
    iframe.allow = "fullscreen";

    mapContainer.innerHTML = "";
    mapContainer.appendChild(iframe);

    console.log("Windy map loaded for:", { lat, lon, temp });
  }, 200);
}
