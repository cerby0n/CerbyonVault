import { useEffect, useState } from "react";
import { Certificate, PrivateKey, Team } from "../types";
import TeamsSelect from "../utils/TeamsSearch";
import { useCertService } from "../utils/useCertService";
import {
  CalendarDays,
  Globe,
  KeyRound,
  LockKeyhole,
  MessageSquare,
  Users,
  X,
} from "lucide-react";
import { formatDate } from "../utils/utils";
import { useItemFetch } from "../hooks/useItemFetch";
import Select from "react-select";

interface SidePanelKeyProps {
  isOpen: boolean;
  onClose: () => void;
  data: { privateKey?: PrivateKey };
  onUpdated: () => void;
}

export default function SidePanelKey({
  isOpen,
  onClose,
  data,
  onUpdated,
}: SidePanelKeyProps) {
  const { updateKey } = useCertService();
  const { fetchCerts, certs } = useItemFetch();
  const [name, setName] = useState<string>(data?.privateKey?.name || "");
  const [certsLoaded, setCertsLoaded] = useState(false);
  const [selectedCert, setSelectedCert] = useState<Certificate | null>(null);
  const [comment, setComment] = useState<string>(
    data?.privateKey?.comment || ""
  );
  const [accessTeams, setAccessTeams] = useState<Team[]>(
    data.privateKey?.access_teams || []
  );

  useEffect(() => {
    if (!certsLoaded) {
      fetchCerts().then(() => setCertsLoaded(true));
    }
  }, [certsLoaded]);

  useEffect(() => {
    if (data.privateKey) {
      setName(data.privateKey.name);
      setComment(data.privateKey.comment || "");
      setAccessTeams(data.privateKey.access_teams);
    }
  }, [data.privateKey]);

  useEffect(() => {
    if (data.privateKey && certsLoaded) {
      const matchedCert = certs.find(
        (c) => c.id === data.privateKey?.certificate?.id
      );
      setSelectedCert(matchedCert || null);
    }
  }, [certsLoaded, certs, data.privateKey]);

  if (!isOpen || !data.privateKey) return null;

  const handleUpdate = async () => {
    try {
      const payload = {
        name,
        comment,
        access_teams: accessTeams.map((t) => t.id),
        certificate: selectedCert?.id || null,
      };
      console.log("payload: ", payload);
      await updateKey(data.privateKey!.id, payload);
      onClose();
      onUpdated();
    } catch (err) {
      console.error("Failed to udpdate Private Key:", err);
    }
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
          <KeyRound size={25} className="text-primary" />
        </div>
        <div className="flex-1">
          <input
            className=" w-full border border-neutral rounded-md p-1 text-lg "
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Key Name"
          />
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <Globe size={25} className="text-primary" />
        <div className="flex flex-col space-y-1 w-full">
          <label className="label">Associated Certificate</label>
          <Select
            value={selectedCert}
            onChange={(value) => setSelectedCert(value as Certificate)}
            options={certs}
            getOptionLabel={(c) => c.name}
            getOptionValue={(c) => c.id.toString()}
            placeholder="Select certificate"
            className="text-gray-900 text-base"
            isClearable
            styles={{
              menuList: (provided) => ({
                ...provided,
                maxHeight: 150,
                overflowY: "auto",
              }),
            }}
          />
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
          <div className="font-semibold">Created at</div>
          <div className=" text-lg">
            {formatDate(data.privateKey.created_at)}
          </div>
        </div>
        <div className="divider lg:divider-horizontal"></div>
        <div>
          <LockKeyhole size={25} className="text-primary" />
        </div>
        <div className="p-2">
          <div className="font-semibold">Key Size</div>
          <div className=" text-lg">{data.privateKey.keysize} bits</div>
        </div>
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
