import { saveAs } from "file-saver";
import useAxios from "../axios/useAxios";
import { useToast } from "../components/ToastProvider";

export const useExportActions = () => {
  const axiosInstance = useAxios();
  const { notify } = useToast();

  const buildExportUrl = (
    certId: number,
    variant: string,
    fmt: string,
    password: string = ""
  ): string => {
    const base = `/certificates/${certId}/export/`;
    const params = new URLSearchParams();
    if (variant.includes("key")|| fmt === "pfx") params.append("key", "true");
    if (variant.includes("chain")) params.append("chain", "true");
    if (fmt === "pfx") params.append("pwd", password);
    params.append("fmt", fmt);
    return `${base}?${params.toString()}`;
  };

  const copyToClipboard = async (url: string) => {
    try {
      const res = await axiosInstance.get(url, { responseType: "text" });
      await navigator.clipboard.writeText(res.data);
      notify("📋 Certificate copied to clipboard!","success");
    } catch (error) {
      notify("Failed to copy to clipboard","error");
    }
  };

  const downloadFile = async (url: string, fileName: string, extension: string) => {
    try {
      const res = await axiosInstance.get(url, { responseType: "blob" });
      const fullName = `${fileName}.${extension}`;
      saveAs(res.data, fullName);
      notify(`Downloaded ${fileName}.${extension} 💾`,"success");
    } catch (error) {
      notify("Failed to download","error");
    }
  };

  return {
    buildExportUrl,
    copyToClipboard,
    downloadFile,
  };
};
