import { PiCertificateThin } from "react-icons/pi";
import { Certificate } from "../../types";

interface CertificateNodeProps {
  cert: Certificate;
}

export default function CertificateNode({ cert }: CertificateNodeProps) {
  return (
    <div className="flex justify-between items-center select-none text-secondary-content">
      <div className="flex items-center gap-3">
        <PiCertificateThin size={30} strokeWidth={8} />
        <div className="flex flex-col flex-1 min-w-0">
          <div className="text-base truncate">{cert.name}</div>
          <div className="text-xs truncate ">
            Expires: {new Date(cert.not_after).toLocaleDateString()}
          </div>
        </div>
      </div>

      <div className="flex items-end justify-end gap-2 flex-shrink-0 min-w-[190px]">
        <div className="text-sm font-semibold ml-12">{cert.certificate_type}</div>
        <div className="flex items-center gap-2 text-right font-semibold mr-4">
          <span
            className={`h-3 w-3 mt-1 rounded-full ${
              cert.is_expired ? "bg-error" : "bg-success"
            }`}
          ></span>
          <div
            className={`font-semibold ${
              cert.is_expired ? "text-error" : "text-success"
            }`}
          >
            {cert.is_expired ? "Expired" : "Valid"}
          </div>
        </div>
      </div>
    </div>
  );
}
