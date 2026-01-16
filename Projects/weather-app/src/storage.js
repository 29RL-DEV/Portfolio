/**
 * Storage Module - Manages localStorage for persistent data
 * Handles search history and user preferences
 */

const STORAGE_KEYS = {
  SEARCH_HISTORY: "weatherapp_search_history",
  TEMPERATURE_UNIT: "weatherapp_temp_unit",
  LAST_CITY: "weatherapp_last_city",
  LAST_COORDS: "weatherapp_last_coords",
};

/**
 * Get search history from localStorage
 * @returns {Array} Array of city search strings
 */
export function getSearchHistory() {
  try {
    const history = localStorage.getItem(STORAGE_KEYS.SEARCH_HISTORY);
    return history ? JSON.parse(history) : [];
  } catch (err) {
    console.error("Failed to load search history:", err);
    return [];
  }
}

/**
 * Add city to search history (max 10 recent)
 * @param {string} city - City display name
 */
export function addToSearchHistory(city) {
  try {
    let history = getSearchHistory();
    // Remove duplicate if exists
    history = history.filter((c) => c !== city);
    // Add to front
    history.unshift(city);
    // Keep only 10 most recent
    history = history.slice(0, 10);
    localStorage.setItem(STORAGE_KEYS.SEARCH_HISTORY, JSON.stringify(history));
  } catch (err) {
    console.error("Failed to save search history:", err);
  }
}

/**
 * Get user's temperature unit preference
 * @returns {boolean} true for Celsius, false for Fahrenheit
 */
export function getTemperatureUnit() {
  try {
    const unit = localStorage.getItem(STORAGE_KEYS.TEMPERATURE_UNIT);
    return unit === null ? true : unit === "celsius";
  } catch (err) {
    console.error("Failed to load temperature unit:", err);
    return true;
  }
}

/**
 * Set user's temperature unit preference
 * @param {boolean} isCelsius - true for Celsius, false for Fahrenheit
 */
export function setTemperatureUnit(isCelsius) {
  try {
    localStorage.setItem(
      STORAGE_KEYS.TEMPERATURE_UNIT,
      isCelsius ? "celsius" : "fahrenheit"
    );
  } catch (err) {
    console.error("Failed to save temperature unit:", err);
  }
}

/**
 * Save last viewed city and coordinates
 * @param {string} city - City name
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 */
export function saveLastCity(city, lat, lon) {
  try {
    localStorage.setItem(STORAGE_KEYS.LAST_CITY, city);
    localStorage.setItem(
      STORAGE_KEYS.LAST_COORDS,
      JSON.stringify({ lat, lon })
    );
  } catch (err) {
    console.error("Failed to save last city:", err);
  }
}

/**
 * Get last viewed city and coordinates
 * @returns {Object|null} {city, lat, lon} or null if not found
 */
export function getLastCity() {
  try {
    const city = localStorage.getItem(STORAGE_KEYS.LAST_CITY);
    const coords = localStorage.getItem(STORAGE_KEYS.LAST_COORDS);

    if (city && coords) {
      const { lat, lon } = JSON.parse(coords);
      return { city, lat, lon };
    }
    return null;
  } catch (err) {
    console.error("Failed to load last city:", err);
    return null;
  }
}

/**
 * Clear all stored data
 */
export function clearAllStorage() {
  try {
    Object.values(STORAGE_KEYS).forEach((key) => {
      localStorage.removeItem(key);
    });
  } catch (err) {
    console.error("Failed to clear storage:", err);
  }
}
