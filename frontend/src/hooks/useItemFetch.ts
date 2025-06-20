import { useState } from "react";
import { Certificate, PrivateKey } from "../types";
import useAxios from "../axios/useAxios";
import { useToast } from "../components/ToastProvider";

export function useItemFetch() {
  const axiosInstance = useAxios()
  const { notify } = useToast();
  const [keys, setKeys] = useState<PrivateKey[]>([]);
  const [certs, setCerts] = useState<Certificate[]>([]);

  async function fetchKeys() {
    try {
      const res = await axiosInstance.get<PrivateKey[]>("/keys");
      setKeys(Array.isArray(res.data) ? res.data : []);
    } catch {
      notify("❌ Failed to load private keys.","error");
    }
  }

  async function fetchCerts() {
    try {
      const res = await axiosInstance.get<Certificate[]>("/certificates");
      setCerts(Array.isArray(res.data) ? res.data : []);
    } catch {
      notify("❌ Failed to load certificates.","error");
    }
  }

  return {
    certs,
    keys,
    fetchCerts,
    fetchKeys,
  };
};
