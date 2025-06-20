
import useAxios from "../axios/useAxios";
import { useToast } from "../components/ToastProvider";

export function useCertService() {
  const axiosInstance = useAxios()
  const { notify } = useToast();

  // API call for importing certificates
  const importCertificates = async (payload: any) => {
    const res = await axiosInstance.post("/import-cert-metadata/", payload, {
      withCredentials: true,
    });
    return res.data;
  };


  // API call for uploading certificate file
  const uploadCertFile = async (file: File, password?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (password) {
      formData.append("password", password);
    }

    try {
      const res = await axiosInstance.post("/upload-cert-file/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        withCredentials: true,
      });
      return res.data;
    } catch (err) {
      console.error("UPLOAD ERROR", err);
      throw new Error("Upload failed or password wrong.");
    }
  };
  // Delete selected certificates
  const deleteCertificates = async (selectedItems: number[]) => {
    try {
      await axiosInstance.delete("/certificates/delete/", {
        data: { ids: selectedItems },
      });
    } catch (err) {
      throw new Error("Failed to delete certificates.");
    }
  };

  // Delete selected Keys
  const deletePrivateKeys = async (selectedItems: number[]) => {
    try {
      await axiosInstance.delete("/keys/delete/", { data: { ids: selectedItems } });
    } catch (err) {
      throw new Error("Failed to delete keys.");
    }
  };

  const updateCertificate = async (certificateId: number, data:{name?:string;comment?:string;access_teams?:number[]}) => {
    try {
      const response = await axiosInstance.patch(
        `/certificates/${certificateId}/update-certificate/`,
        data
      );
      console.log("Certificate updated:", response.data);
      notify("Certificate upadated successfully","success")
      return response.data;
    } catch (error) {
      notify("Error updating certificate:", "error");
      throw error;
    }
  };

  const updateKey = async (keyId: number, data:{name?:string;comment?:string;access_teams?:number[]}) => {
    try {
      const response = await axiosInstance.patch(
        `/keys/${keyId}/update-privatekey/`,
        data
      );
      notify("Private Key upadated successfully","success")
      return response.data;
    } catch (error) {
      notify("Error updating Private Key:", "error");
      throw error;
    }
  };

  const exportCert = async(certificateId: number, options:{format:"pem" | "crt"; includeChain?: boolean}):Promise<Blob> => {
    const {format, includeChain=false} = options;
    const response = await axiosInstance.get(`/certificates/${certificateId}/export/`,{
      params: {
        fmt: format,
        chain: includeChain
      },
      responseType: "blob",
      withCredentials: true
    });
    return response.data
  }

  const exportCertWithKey = async (
    certificateId: number,
    options: { format: "pem"; includeChain?: boolean }
  ): Promise<Blob> => {
    const { format, includeChain = false } = options;
    const response = await axiosInstance.get(`/certificates/${certificateId}/export/`, {
      params: {
        fmt: format,
        chain: includeChain,
        key: true,
      },
      responseType: "blob",
      withCredentials: true,
    });
    return response.data;
  };

  const exportCertPfx = async (
    certificateId: number,
    options: { includeChain?: boolean; password?: string }
  ): Promise<Blob> => {
    const { includeChain = false, password = "" } = options;
    const response = await axiosInstance.get(`/certificates/${certificateId}/export/`, {
      params: {
        fmt: "pfx",
        chain: includeChain,
        key: true,
        password,
      },
      responseType: "blob",
      withCredentials: true,
    });
    return response.data;
  };

  return {
    exportCert,
    exportCertWithKey,
    exportCertPfx,
    importCertificates,
    uploadCertFile,
    deleteCertificates,
    deletePrivateKeys,
    updateCertificate,
    updateKey,
  };
}