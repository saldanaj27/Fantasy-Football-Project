import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://0.0.0.0:8000/api/",
});

export default api;
