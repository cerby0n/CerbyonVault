import { FaKey } from "react-icons/fa";
import { PiCertificateThin } from "react-icons/pi";
import { PrivateKey } from "../../types";

interface PrivateKeyNodeProps {
  privateKey: PrivateKey;
  selectedIds: number[];
  onClick: (e: React.MouseEvent, privateKey: PrivateKey, selectedIds: number[]) => void;
  onDoubleClick: () => void;
}

export default function PrivateKeyNode({
  privateKey,
  selectedIds,
  onClick,
  onDoubleClick,
}: PrivateKeyNodeProps) {
  const isSelected = selectedIds.includes(privateKey.id);
  return (
    <li>
      <div
        onClick={(e) => onClick(e, privateKey, selectedIds)}
        onDoubleClick={onDoubleClick}
        className={`cursor-pointer border-b border-neutral/75 hover:rounded hover:bg-secondary/25 mt-2 hover:border-none mr-2 ${
          isSelected ? "bg-secondary/25  border-none rounded " : ""
        }`}
      >
        <div className="flex justify-between items-center select-none text-secondary-content">
          <div className="ml-5 flex-1 flex items-center gap-3">
            <FaKey size={30} />
            <div>
              <div className="text-base truncate">{privateKey.name}</div>
              <div className="text-xs truncate">
                Uploaded: {new Date(privateKey.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
          {privateKey.certificate && (
            <div className="flex-1 flex items-center gap-2 flex-shrink-0 min-w-[190px]">
              <PiCertificateThin size={30} strokeWidth={8} />
              <div className="">
                {privateKey.certificate?.name}
              </div>
            </div>
          )}
          <div className="mr-4 truncate">
            <div className="text-sm ">{privateKey.keysize} bits</div>
          </div>
        </div>
        
      </div>
    </li>
  );
}
