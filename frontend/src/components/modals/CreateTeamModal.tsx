import { useState } from "react";
import useAxios from "../../axios/useAxios";
import { useToast } from "../ToastProvider";
import { useNavigate } from "react-router-dom";

export default function CreateTeamModal({ onClose, onCreated }: any) {
  const axiosInstance = useAxios();
  const { notify } = useToast();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleCreate = async () => {
    setError("");
    if (!name) {
      setError("Team name cannot be empty.");
      return;
    }

    try {
      const res = await axiosInstance.post("/admin/teams/", { name });
      notify("✅ Team created", "success");
      onCreated(res.data);
      navigate(`/admin/teams/${res.data.id}`);
    } catch (err: any) {
      if (err.response?.data?.name) {
        setError("⚠️ A team with this name already exists.");
      } else {
        setError("❌ Failed to create team.");
      }
    }
  };

  return (
    <dialog open className="modal backdrop-blur-xs">
      <div className="modal-box">
        <input
          type="text"
          placeholder="Team name"
          className="input focus:outline-none w-full my-4"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {error && <p className="text-red-500 text-sm mb-2">{error}</p>}

        <div className="modal-action">
          <button className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleCreate}>
            Create
          </button>
        </div>
      </div>
    </dialog>
  );
}