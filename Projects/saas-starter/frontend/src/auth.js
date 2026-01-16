export const getToken = () => {
  return sessionStorage.getItem("access");
};

export const setToken = (token) => {
  sessionStorage.setItem("access", token);
};

export const clearToken = () => {
  sessionStorage.removeItem("access");
};
