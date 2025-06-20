import { useEffect, useState } from "react";
import { Certificate, Team } from "../types";
import TeamsSelect from "../utils/TeamsSearch";
import WebsitesManager from "./items/WebsitesManager";
import { useCertService } from "../utils/useCertService";
import { formatDate } from "../utils/utils";
import { InputCopy } from "./items/InputCopy";
import {
  CalendarDays,
  FileBadge,
  Globe,
  Hash,
  MessageSquare,
  Stamp,
  Tag,
  Users,
  X,
} from "lucide-react";


interface SidePanelCertProps {
  isOpen: boolean;
  onClose: () => void;
  data: { cert?: Certificate };
  onUpdated: () => void;
}

export default function SidePanelCert({
  isOpen,
  onClose,
  data,
  onUpdated,
}: SidePanelCertProps) {
  const { updateCertificate } = useCertService();
  const [activeSan, setActiveSan] = useState<string | null>(null);
  const [name, setName] = useState<string>(data?.cert?.name || "");
  const [comment, setComment] = useState<string>(data?.cert?.comment || "");
  const [accessTeams, setAccessTeams] = useState<Team[]>(
    data.cert?.access_teams || []
  );

  useEffect(() => {
    if (data.cert) {
      setName(data.cert.name);
      setComment(data.cert.comment || "");
      setAccessTeams(data.cert.access_teams);
    }
  }, [data.cert]);

  if (!isOpen || !data.cert) return null;

  const handleUpdate = async () => {
    try {
      const payload = {
        name,
        comment,
        access_teams: accessTeams.map((t) => t.id),
      };
      await updateCertificate(data.cert!.id, payload);
      onClose();
      onUpdated();
    } catch (err) {
      console.error("Failed to udpdate certificate:", err);
    }
  };

  const handleClick = (san: string) => {
    navigator.clipboard.writeText(san).then(() => {
      setActiveSan(san);
      setTimeout(() => setActiveSan(null), 1000);
    });
  };

  return (   
    <div className="p-4 space-y-8 select-none max-h-[calc(100vh-64px)] overflow-y-auto">
      <div className="flex justify-end mb-4">
        <button onClick={onClose} className="all-[unset]">
          <X
            size={25}
            strokeWidth={3}
            className="
              text-primary/75 
              cursor-pointer 
              transition-transform duration-200 
              transform hover:scale-120 hover:text-primary
            "
          />
        </button>
      </div>
      <div className="flex items-center space-x-2">
        <div>
          <FileBadge size={25} className="text-primary" />
        </div>
        <div className="flex-1">
          <input
            className=" w-full border border-neutral rounded-md p-1 text-lg "
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Certificate Name"
          />
        </div>
      </div>
      <div className="flex items-center space-x-2 ">
        <div>
          <Stamp size={25} className="text-primary" />
        </div>
        <div className="w-full">
          <label className="label">Issuer</label>
          <InputCopy value={data.cert.issuer} />
        </div>
      </div>
      <div className="flex items-center space-x-2 ">
        <div>
          <Hash size={25} className="text-primary" />
        </div>
        <div className="w-full">
          <label className="label">Serial Number</label>
          <InputCopy value={data.cert.serial_number} />
        </div>
      </div>
    
      <div className="flex items-center space-x-2 ">
        <div>
          <MessageSquare size={25} className="text-primary" />
        </div>

        <textarea
          className=" border border-neutral rounded-md p-2 w-full"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Add a comment"
        />
      </div>
      <div className="flex items-center space-x-2">
        <div>
          <CalendarDays size={25} className="text-primary" />
        </div>
        <div className="p-2">
          <div className="font-semibold">Not Before</div>
          <div className=" text-lg">{formatDate(data.cert.not_before)}</div>
        </div>
        <div className="divider lg:divider-horizontal"></div>
        <div className="p-2">
          <div className="font-semibold">Not After</div>
          <div className=" text-lg">{formatDate(data.cert.not_after)}</div>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <div>
          <Tag size={25} className="text-primary" />
        </div>
        <div className="border-neutral border rounded-md p-2 flex-1">
          {/* ← conditional rendering starts here */}
          {data.cert.san.length > 0 ? (
            <>
            <div className="label mb-2">Subject Alternative Name</div>
            <div className="grid grid-cols-2 gap-2">
              {data.cert.san.map((san) => {
                const isActive = activeSan === san;
                return (
                  <button
                    key={san}
                    onClick={() => handleClick(san)}
                    className={`
                w-full flex items-center px-1 py-0.5 
                bg-accent/50 rounded-lg cursor-pointer hover:bg-accent/70
                ${
                  isActive
                    ? "border-primary ring-2 ring-primary"
                    : "border-neutral hover:border-neutral-content"
                }
                focus:outline-none
              `}
                  >
                    <span className="flex-1 truncate text-sm text-secondary-content">
                      {san}
                    </span>
                  </button>
                );
              })}
            </div>
            </>
          ) : (
            <p className="text-sm text-secondary-content/50 italic">
              No Subject Alternative Names found.
            </p>
          )}
          {/* ← conditional rendering ends here */}
        </div>
      </div>
      <div className="flex items-center space-x-2 ">
        <div>
          <Globe size={25} className="text-primary" />
        </div>
        <WebsitesManager
          certId={data.cert.id}
          initialWebsites={data.cert.websites}
          onWebsitesUpdated={onUpdated}
        />
        
      </div>
      <div className="flex items-center space-x-2">
        <div>
          <Users size={25} className="text-primary" />
        </div>
        <div className="w-full">
          <label className="label">Assign Teams</label>
          <TeamsSelect value={accessTeams} onChange={setAccessTeams} />
        </div>
      </div>
      <div className="w-full flex justify-end">
      <button className="btn btn-primary" onClick={handleUpdate}>
        Update Certificate
      </button>
    </div>
    </div>
  );
}
