import axios from "axios";

/**
 * RENDER BACKEND URL
 */
const BASE_URL =
  process.env.REACT_APP_API_URL || "https://todo-manager-api-ux4e.onrender.com";

/**
 * API instance
 */
const API = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Add JWT access token to all requests
 */
API.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");
  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

/**
 * Auto refresh JWT when expired
 */
API.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refresh = localStorage.getItem("refresh");
        if (!refresh) throw new Error("No refresh token");

        const res = await axios.post(
          `${BASE_URL}/api/token/refresh/`,
          { refresh },
          {
            headers: { "Content-Type": "application/json" },
          },
        );

        localStorage.setItem("access", res.data.access);
        originalRequest.headers.Authorization = `Bearer ${res.data.access}`;

        return API(originalRequest);
      } catch (err) {
        localStorage.clear();
        window.location.href = "/";
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  },
);

/**
 * TASKS API
 */
export const taskAPI = {
  getAll: () =>
    API.get("/tasks/").then((r) =>
      Array.isArray(r.data) ? r.data : r.data?.results || [],
    ),

  create: (data) => API.post("/tasks/", data).then((r) => r.data),

  update: (id, data) => API.put(`/tasks/${id}/`, data).then((r) => r.data),

  delete: (id) => API.delete(`/tasks/${id}/`),
};

/**
 * AUTH API
 */
export const authAPI = {
  login: (username, password) =>
    API.post("/token/", { username, password }).then((r) => r.data),

  register: (data) => API.post("/auth/register/", data).then((r) => r.data),

  getMe: () => API.get("/auth/me/").then((r) => r.data),

  updateMe: (data) => API.put("/auth/me/", data).then((r) => r.data),
};

export default API;
