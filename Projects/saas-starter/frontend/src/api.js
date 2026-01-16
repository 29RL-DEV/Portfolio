const API_URL = process.env.REACT_APP_API_URL;

if (!API_URL) {
  throw new Error("API URL missing – check environment variables");
}

export default API_URL;

export async function login(email, password) {
  const res = await fetch(`${API_URL}/api/login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  return res.json();
}
