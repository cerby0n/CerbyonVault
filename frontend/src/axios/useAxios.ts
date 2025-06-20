
import dayjs from "dayjs";
import {jwtDecode} from "jwt-decode";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

interface DecodedToken { exp: number}


export default function useAxios(){
  const baseURL = import.meta.env.VITE_API_URL;
  const {authTokens, setUser, setAuthTokens} = useAuth()

  const axiosInstance = axios.create({
    baseURL: baseURL,
    headers: { Authorization: authTokens ? `Bearer ${authTokens.access}` : ""},
  });

  axiosInstance.interceptors.request.use(async (req) => {
    if (!authTokens) return req
    const user = jwtDecode<DecodedToken>(authTokens.access);
    const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;
    if (!isExpired) return req;
    const refreshToken = authTokens.refresh
    const response = await axios.post(`${baseURL}/token/refresh/`, {
      refresh: refreshToken,
    });

    localStorage.setItem("authTokens", JSON.stringify(response.data));

    setAuthTokens(response.data);
    setUser(jwtDecode(response.data.access));

    req.headers.Authorization = `Bearer ${response.data.access}`;

    return req;
  });

  return axiosInstance;
};


