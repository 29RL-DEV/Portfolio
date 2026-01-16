/**
 * UI Module - Handles all DOM manipulation and user interface
 */

/**
 * Format date to readable string
 * @param {Date} date - Date object
 * @returns {string} Formatted date string
 */
export function formatDate(date) {
  const options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  return date.toLocaleDateString("en-US", options);
}

/**
 * Show or hide loading spinner
 * @param {boolean} show - True to show, false to hide
 */
export function showSpinner(show) {
  const spinner = document.getElementById("loadingSpinner");
  if (show) {
    spinner.classList.remove("hidden");
  } else {
    spinner.classList.add("hidden");
  }
}

/**
 * Show error message to user
 * @param {string} message - Error message text
 */
export function showErrorMsg(message) {
  const errorBox = document.getElementById("errorMessage");
  const errorText = document.getElementById("errorText");

  errorText.textContent = message || "An error occurred. Please try again.";
  errorBox.classList.remove("hidden");
}

/**
 * Hide error message
 */
export function hideError() {
  const errorBox = document.getElementById("errorMessage");
  errorBox.classList.add("hidden");
}

/**
 * Show or hide weather data sections
 * @param {boolean} show - True to show weather, false to show empty state
 */
export function showData(show) {
  const weatherSection = document.getElementById("currentWeather");
  const forecastSection = document.getElementById("forecastSection");
  const emptyState = document.getElementById("emptyState");

  if (show) {
    weatherSection.classList.remove("hidden");
    forecastSection.classList.remove("hidden");
    emptyState.classList.add("hidden");
  } else {
    weatherSection.classList.add("hidden");
    forecastSection.classList.add("hidden");
    emptyState.classList.remove("hidden");
  }
}

/**
 * Display city suggestions
 * @param {Array} cities - Array of city objects
 * @param {Function} onSelect - Callback when city is selected
 */
export function displaySuggestions(cities, onSelect) {
  const cityList = document.getElementById("suggestions");
  cityList.innerHTML = "";

  if (!cities || cities.length === 0) {
    cityList.innerHTML =
      '<li style="color: var(--danger);">No cities found</li>';
    return;
  }

  // Show max 8 results
  cities.slice(0, 8).forEach((city) => {
    const li = document.createElement("li");
    const display = `${city.name}${city.state ? ", " + city.state : ""}, ${
      city.country
    }`;
    li.textContent = display;

    li.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      cityList.innerHTML = "";
      onSelect(city, display);
    });

    cityList.appendChild(li);
  });
}

/**
 * Clear suggestions list
 */
export function clearSuggestions() {
  const cityList = document.getElementById("suggestions");
  cityList.innerHTML = "";
}

/**
 * Display current weather information
 * @param {Object} data - Weather data from API
 * @param {string} cityName - City display name
 * @param {boolean} isCelsius - Temperature unit
 */
export function displayCurrentWeather(data, cityName, isCelsius) {
  const current = data.current;
  const daily = data.daily;

  // Get weather info (will be imported from api module)
  // Temp conversion
  const tempC = Math.round(current.temperature_2m);
  const temp = isCelsius ? tempC : Math.round((tempC * 9) / 5 + 32);
  const feelsC = Math.round(current.apparent_temperature);
  const feels = isCelsius ? feelsC : Math.round((feelsC * 9) / 5 + 32);

  // Display current weather
  document.getElementById("cityName").textContent = cityName;
  document.getElementById("weatherDate").textContent = formatDate(new Date());
  document.getElementById("temperature").textContent = temp;
  document.getElementById("feelsLike").textContent = feels;
  document.getElementById("humidity").textContent =
    current.relative_humidity_2m + "%";
  document.getElementById("pressure").textContent =
    (current.pressure_msl / 100).toFixed(0) + " hPa";
  document.getElementById("visibility").textContent =
    (current.visibility / 1000).toFixed(1) + " km";

  // Max/Min temps
  const maxC = Math.round(daily.temperature_2m_max[0]);
  const minC = Math.round(daily.temperature_2m_min[0]);
  const maxTemp = isCelsius ? maxC : Math.round((maxC * 9) / 5 + 32);
  const minTemp = isCelsius ? minC : Math.round((minC * 9) / 5 + 32);

  document.getElementById("maxTemp").textContent = maxTemp + "°";
  document.getElementById("minTemp").textContent = minTemp + "°";
}

/**
 * Display 5-day forecast
 * @param {Object} data - Weather data from API
 * @param {boolean} isCelsius - Temperature unit
 */
export function displayForecast(data, isCelsius) {
  const daily = data.daily;
  const forecastContainer = document.getElementById("forecastContainer");
  forecastContainer.innerHTML = "";

  // Show 5 days
  for (let i = 1; i < 6; i++) {
    const date = new Date();
    date.setDate(date.getDate() + i);

    const maxC = Math.round(daily.temperature_2m_max[i]);
    const minC = Math.round(daily.temperature_2m_min[i]);
    const maxTemp = isCelsius ? maxC : Math.round((maxC * 9) / 5 + 32);
    const minTemp = isCelsius ? minC : Math.round((minC * 9) / 5 + 32);

    const card = document.createElement("div");
    card.className = "forecast-card";
    card.innerHTML = `
      <div class="forecast-date">${date.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      })}</div>
      <div class="forecast-temp"><strong>${maxTemp}°</strong> / ${minTemp}°</div>
    `;

    forecastContainer.appendChild(card);
  }
}

/**
 * Update temperature unit display
 * @param {boolean} isCelsius - True for Celsius, false for Fahrenheit
 */
export function updateUnitDisplay(isCelsius) {
  const unitDisplay = document.getElementById("unitDisplay");
  const tempUnitSpan = document.getElementById("tempUnit");
  const feelsUnitSpan = document.getElementById("feelsLikeUnit");

  const unit = isCelsius ? "°C" : "°F";
  unitDisplay.textContent = unit;
  tempUnitSpan.textContent = unit;
  feelsUnitSpan.textContent = unit;
}

/**
 * Get search input value
 * @returns {string} Input value
 */
export function getSearchInput() {
  const input = document.getElementById("searchInput");
  return input.value.trim();
}

/**
 * Set search input value
 * @param {string} value - Value to set
 */
export function setSearchInput(value) {
  const input = document.getElementById("searchInput");
  input.value = value;
}

/**
 * Clear search input
 */
export function clearSearchInput() {
  const input = document.getElementById("searchInput");
  input.value = "";
  input.focus();
}

/**
 * Focus search input
 */
export function focusSearchInput() {
  const input = document.getElementById("searchInput");
  input.focus();
}
