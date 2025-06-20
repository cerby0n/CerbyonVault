import { useState, FormEvent, useEffect } from "react";
import useAxios from "../../axios/useAxios";
import { Website } from "../../types/index";
import { Pencil, Plus, Save, Trash2, X } from "lucide-react";
import ConfirmModal from "../modals/ConfirmModal";

interface WebsitesManagerProps {
  certId: number;
  initialWebsites: Website[];
  onWebsitesUpdated: () => void;
}

export default function WebsitesManager({
  certId,
  initialWebsites,
  onWebsitesUpdated,
}: WebsitesManagerProps) {
  const axios = useAxios();
  const [websites, setWebsites] = useState<Website[]>(initialWebsites);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formUrl, setFormUrl] = useState<string>("");
  const [newUrl, setNewUrl] = useState<string>("");

  useEffect(() => {
    setWebsites(initialWebsites);
    setEditingId(null);
    setFormUrl("");
    setNewUrl("");
  }, [initialWebsites]);

  const refresh = async () => {
    try {
      const response = await axios.get(`certificates/${certId}/`);
      setWebsites(response.data.websites);
      onWebsitesUpdated();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`websites/${id}/`);
      await refresh();
    } catch (error) {
      alert(`Delete failed: ${error}`);
    }
  };

  const startEdit = (site: Website) => {
    setEditingId(site.id);
    setFormUrl(site.url);
  };

  const saveEdit = async (e: FormEvent) => {
    e.preventDefault();
    if (editingId === null) return;
    try {
      await axios.put(`websites/${editingId}/`, {
        url: formUrl,
        certificate: certId,
      });
      setEditingId(null);
      setFormUrl("");
      await refresh();
    } catch (error) {
      alert(`Update failed: ${error}`);
    }
  };

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`certificates/${certId}/websites/`, { url: newUrl });
      setNewUrl("");
      await refresh();
    } catch (error) {
      alert(`Add failed: ${error}`);
    }
  };

  return (
    <div className="space-y-4 overflow-auto border-neutral border rounded-md p-2 w-full">
      
      {websites.length > 0 ? (
        <>
        <div className="label mb-0">Websites</div>
        <ul className="space-y-2">
          {websites.map((site) => (
            <li key={site.id} className="flex items-center space-x-3">
              {editingId === site.id ? (
                <form onSubmit={saveEdit} className="flex-1 flex space-x-2">
                  <input
                    type="url"
                    className="flex-1 border rounded p-2"
                    value={formUrl}
                    onChange={(e) => setFormUrl(e.target.value)}
                    required
                  />
                  <button type="submit" className="px-2 py-1 btn-success btn">
                    <Save size={15} />
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingId(null)}
                    className="px-2 py-1 btn btn-neutral"
                  >
                    <X size={15} />
                  </button>
                </form>
              ) : (
                <>
                  <a
                    href={site.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 text-primary hover:underline"
                  >
                    {site.domain}
                  </a>
                  <button
                    onClick={() => startEdit(site)}
                    className="px-2 btn btn-primary "
                  >
                    <Pencil size={15} className="text-primary-content" />
                  </button>
                  <button
                    onClick={() =>setShowConfirmModal(true)}
                    className="px-2 btn btn-error"
                  >
                    <Trash2 size={15} className="text-error-content" />
                  </button>
                  {showConfirmModal && (
                <ConfirmModal
                  message={
                    <>
                      Are you sure you want to delete this site ?
                      <br />
                      This action cannot be undone.
                    </>
                  }
                  onCancel={() => setShowConfirmModal(false)}
                  onConfirm={() => handleDelete(site.id)}
                />
              )}
                </>
              )}
            </li>
          ))}
        </ul>
        </>
      ) : (
        <p className="text-gray-500">No websites attached yet.</p>
      )}
      <form onSubmit={handleAdd} className=" flex space-x-2">
        <input
          type="url"
          placeholder="https://example.com"
          className="flex-1 border rounded p-2"
          value={newUrl}
          onChange={(e) => setNewUrl(e.target.value)}
          required
        />
        <button type="submit" className="px-2 py-1 btn btn-primary rounded">
          <Plus size={15} />
        </button>
      </form>
    </div>
  );
}
