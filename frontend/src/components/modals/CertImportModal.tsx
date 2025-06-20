import { useRef, useState } from "react";
import TeamsSelect from "../../utils/TeamsSearch";
import { useCertService } from "../../utils/useCertService";

type Cert = {
  temp_id: string;
  common_name: string;
  subject: string;
  serial: string;
  not_after: string;
};

type PrivateKey = {
  temp_id: string;
  type: string;
  bit_length: number;
  filename: string;
};

type Props = {
  session_key: string;
  certificates: Cert[];
  private_key?: PrivateKey;
  onSubmit: (payload: any) => void;
  onCancel: () => void;
};

type Team = {
  id: number;
  name: string;
};

type URLOption = {
  value: string;
};

export default function CertImportModal({
  session_key,
  certificates=[],
  onSubmit,
  private_key,
  onCancel,
}: Props) {
  const [form, setForm] = useState(() =>
    certificates.map((cert) => ({
      ...cert,
      selected: true,
      name: cert.common_name,
      teams: [] as number[],
      urls: [] as URLOption[],
      errors: [] as string[],
      isAddingUrl: false,
    }))
  );

  const {importCertificates} = useCertService()
  const [includeKey, setIncludeKey] = useState(true);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const inputRefs = useRef<(HTMLInputElement | null)[][]>([]);
  const isFormValid = form.every((cert) => cert.errors.length === 0);

  const handleSubmit = async () => {
    if (!isFormValid) return;

    const selectedCerts = form.filter((f) => f.selected);
    const certs = selectedCerts.map((c) => ({
      temp_id: c.temp_id,
      name: c.name,
      teams: teams.map(t => t.id),
      urls: c.urls.map((url) => url.value),
    }));

    const keyPayload =
      private_key && includeKey
        ? {
            temp_id: private_key.temp_id,
            linked_cert_temp_id: selectedCerts[0]?.temp_id,
            teams: teams.map(t => t.id),
            filename: private_key.filename,
            bit_length: private_key.bit_length,
          }
        : undefined;

    setLoading(true);
    setError("");

    try {
      const payload: any = {
        session_key,
        certs,
        key: keyPayload,
      };
      console.log("Key Payload:", keyPayload);
      console.log("Submitting payload:", payload);
      await importCertificates(payload);
      onSubmit(payload);
    } catch (err: any) {
      setError(err.response?.data?.error || "Import failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleUrlChange = (
    certIndex: number,
    urlIndex: number,
    value: string
  ) => {
    const urlRegex =
      /^(http|https):\/\/[a-zA-Z0-9-_.]+(\.[a-zA-Z]{2,})+([/?].*)?$/;
    const isValidUrl = urlRegex.test(value);

    setForm((prevForm) =>
      prevForm.map((cert, index) =>
        index === certIndex
          ? {
              ...cert,
              urls: cert.urls.map((url, i) =>
                i === urlIndex ? { ...url, value } : url
              ),
              errors: isValidUrl
                ? [] 
                : [
                    "Please enter a valid URL starting with http:// or https://",
                  ], 
            }
          : cert
      )
    );
  };

  const handleAddUrl = (certIndex: number) => {
    setForm((prevForm) =>
      prevForm.map((cert, index) =>
        index === certIndex
          ? {
              ...cert,
              isAddingUrl: true,
              urls: [...cert.urls, { value: "", errors: [] }], 
            }
          : cert
      )
    );
  };

  const handleRemoveUrl = (certIndex: number, urlIndex: number) => {
    setForm((prevForm) => {
      const updatedForm = prevForm.map((cert, index) => {
        if (index === certIndex) {
          const updatedUrls = cert.urls.filter((_, i) => i !== urlIndex);
          return {
            ...cert,
            urls: updatedUrls,
            isAddingUrl: updatedUrls.length === 0 ? false : cert.isAddingUrl,
            errors: updatedUrls.length === 0 ? [] : cert.errors,
          };
        }
        return cert;
      });
      return updatedForm;
    });
  };

  const handleKeyDown = (
    e: React.KeyboardEvent,
    certIndex: number,
    urlIndex: number
  ) => {
    if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault();
      if (urlIndex === form[certIndex].urls.length - 1) {
        handleAddUrl(certIndex);
      }

      setTimeout(() => {
        if (
          inputRefs.current[certIndex] &&
          inputRefs.current[certIndex][urlIndex + 1]
        ) {
          inputRefs.current[certIndex][urlIndex + 1]?.focus();
        }
      }, 0);
    }
  };

  const handleCheckboxClick = (certIndex: number) => {
    setForm((prevForm) =>
      prevForm.map((cert, index) =>
        index === certIndex ? { ...cert, selected: !cert.selected } : cert
      )
    );
  };

  return (
    <div className="modal modal-open backdrop-blur-xs">
      <div className="modal-box w-full max-w-4xl bg-base-100">
        <h2 className="font-bold text-secondary-content text-xl mb-4">Import Certificates</h2>
        <div className="mb-6">
          <label className="label font-semibold mb-2">Assign Teams</label>
          <TeamsSelect value={teams} onChange={setTeams} />
        </div>
        <div
          className="space-y-4 max-h-64 overflow-y-auto"
          style={{
            maxHeight: "calc(80vh)", 
            overflowY: "auto",
          }}
        >
          {form.map((cert, idx) => (
            <div
              key={cert.temp_id}
              className="flex items-center gap-4 p-4 rounded-md transition"
            >
              {/* Checkbox */}

              <input
                type="checkbox"
                checked={cert.selected}
                className="checkbox size-8"
                onChange={() => handleCheckboxClick(idx)}
              />

              <div
                className="flex items-center gap-4 w-full relative"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Name input */}
                <input
                  type="text"
                  className="input input-bordered  flex-1"
                  placeholder="Certificate name"
                  value={cert.name}
                  onChange={(e) =>
                    setForm((f) =>
                      f.map((item, i) =>
                        i === idx ? { ...item, name: e.target.value } : item
                      )
                    )
                  }
                />
                {/* Show the "Add URL" button if the user is not currently adding a URL */}
                {!cert.isAddingUrl && (
                  <button
                    className="btn btn-primary btn-xs text-primary-content"
                    onClick={() => handleAddUrl(idx)}
                  >
                    Add URL
                  </button>
                )}
                {/* If the user is adding a URL, show the input field */}
                {cert.isAddingUrl && (
                  <div className="flex-1 flex-col gap-2 w-full">
                    {cert.urls.map((url, urlIndex) => (
                      <div
                        key={urlIndex}
                        className="flex items-center gap-2 rounded-lg "
                      >
                        <input
                          type="text"
                          className="input input-bordered flex-1 px-4 rounded-md "
                          value={url.value}
                          onKeyDown={(e) => handleKeyDown(e, idx, urlIndex)}
                          placeholder="Enter URL"
                          onChange={
                            (e) =>
                              handleUrlChange(idx, urlIndex, e.target.value)
                          }
                          ref={(el) => {
                            if (el) {
                              inputRefs.current[idx] =
                                inputRefs.current[idx] || [];
                              inputRefs.current[idx][urlIndex] = el;
                            }
                          }}
                        />
                        <button
                          onClick={() => handleRemoveUrl(idx, urlIndex)}
                          className="btn btn-danger btn-xs"
                        >
                          X
                        </button>
                      </div>
                    ))}
                    {/* Show error message if the URL is invalid */}
                    {cert.errors.length > 0 && (
                      <div className="text-error text-xs mt-1">
                        {cert.errors[0]}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {private_key && (
          <>
            <div className="divider">Private Key</div>
            <div
              className="flex items-center gap-4 p-4 rounded-md transition-colors duration-200"
              onClick={() => setIncludeKey(!includeKey)}
            >
              {/* Checkbox purely visual */}
              <input
                type="checkbox"
                checked={includeKey}
                readOnly
                className="checkbox pointer-events-none"
              />

              {/* Key Info */}
              <div>
                <p className="text-sm text-gray-600 mt-1">
                  {private_key.type} • {private_key.bit_length} bits
                </p>
              </div>
            </div>
          </>
        )}
        {error && <div className="alert alert-error mt-4">{error}</div>}
        <div className="modal-action">
          <button
            onClick={onCancel}
            className="btn btn-outline"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || !isFormValid}
            className="btn btn-primary text-primary-content"
          >
            {loading ? "Importing..." : "Import Selected"}
          </button>
        </div>
      </div>
    </div>
  );
}
