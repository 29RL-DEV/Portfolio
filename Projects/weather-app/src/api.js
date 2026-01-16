/**
 * API Module - Handles all external API calls
 * Uses Open-Meteo (weather) and Nominatim (geocoding)
 */

const WEATHER_API = "https://api.open-meteo.com/v1";
const GEOCODING_API = "https://nominatim.openstreetmap.org/search";

/**
 * Fetch cities from Nominatim geocoding service
 * @param {string} query - City search query
 * @param {AbortSignal} signal - Abort signal for request cancellation
 * @returns {Promise<Array>} Array of city objects with name, lat, lon, country, state
 */
export async function searchCities(query, signal = null) {
  if (!query || query.trim().length === 0) {
    return [];
  }

  try {
    const url = `${GEOCODING_API}?q=${encodeURIComponent(
      query
    )}&format=json&limit=8&addressdetails=1&accept-language=en`;

    const fetchOptions = {
      headers: {
        "Accept-Language": "en",
      },
    };

    if (signal) {
      fetchOptions.signal = signal;
    }

    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error(
          "Too many requests. Please wait a moment and try again."
        );
      }
      throw new Error(`Server error (${response.status}). Try again later.`);
    }

    const data = await response.json();

    // Transform Nominatim response to our format
    return data.map((city) => {
      const address = city.address || {};
      let country = address.country || "";

      if (!country && city.display_name) {
        const parts = city.display_name.split(",");
        if (parts.length > 1) {
          country = parts[parts.length - 1].trim();
        }
      }

      const state = address.state || "";
      const cityName =
        address.city || address.town || address.village || city.name || "";

      return {
        name: cityName,
        lat: parseFloat(city.lat),
        lon: parseFloat(city.lon),
        country: country || "World",
        state: state,
      };
    });
  } catch (err) {
    console.error("City search failed:", err);
    throw err;
  }
}

/**
 * Fetch weather data for given coordinates
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<Object>} Weather data object
 */
export async function fetchWeatherByCoords(lat, lon) {
  try {
    // Check internet connection first
    if (!navigator.onLine) {
      throw new Error("No internet connection. Check your network.");
    }

    const url = `${WEATHER_API}/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,pressure_msl,visibility,temperature_2m_max,temperature_2m_min&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=auto`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error("Unable to fetch weather. Try again later.");
    }

    const data = await response.json();

    if (!data.current) {
      throw new Error("Invalid weather data received.");
    }

    return data;
  } catch (err) {
    console.error("Weather fetch error:", err);
    throw err;
  }
}

/**
 * Convert temperature from Celsius to Fahrenheit
 * @param {number} celsius - Temperature in Celsius
 * @returns {number} Temperature in Fahrenheit
 */
export function celsiusToFahrenheit(celsius) {
  return Math.round((celsius * 9) / 5 + 32);
}

/**
 * Get weather description from WMO weather code
 * @param {number} code - WMO weather code
 * @returns {string} Weather description
 */
export function getWeatherDescription(code) {
  const descriptions = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
  };
  return descriptions[code] || "Unknown";
}

/**
 * Get emoji weather icon from WMO weather code
 * @param {number} code - WMO weather code
 * @returns {string} Weather emoji
 */
export function getWeatherIcon(code) {
  if (code === 0 || code === 1) return "☀️";
  if (code === 2) return "🌤️";
  if (code === 3) return "☁️";
  if ([45, 48].includes(code)) return "🌫️";
  if ([51, 53, 55].includes(code)) return "🌧️";
  if ([61, 63, 65, 80, 81, 82].includes(code)) return "🌧️";
  if ([71, 73, 75, 85, 86].includes(code)) return "❄️";
  if ([95, 96, 99].includes(code)) return "⛈️";
  return "🌤️";
}
