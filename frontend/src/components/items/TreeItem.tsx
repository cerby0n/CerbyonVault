import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { Certificate } from "../../types";
import CertificateNode from "./CertificateNode";

interface TreeItemProps {
  cert: Certificate;
  selectedIds: number[];
  onClick: (e: React.MouseEvent, cert: Certificate) => void;
  onDoubleClick: (cert: Certificate) => void;
  onChildSelect: (e: React.MouseEvent, cert: Certificate) => void;
  onChildDoubleClick: (cert: Certificate) => void;
  onContextMenu?: (e: React.MouseEvent, cert: Certificate) => void;
  isFlat?: boolean;
}

export default function TreeItem({
  cert,
  selectedIds,
  onClick,
  onDoubleClick,
  onChildSelect,
  onChildDoubleClick,
  onContextMenu,
  isFlat,
}: TreeItemProps) {
  const [open, setOpen] = useState(false);
  const isSelected = selectedIds.includes(cert.id);
  
  const handleChildClick = (e: React.MouseEvent, childCert: Certificate) => {
    e.stopPropagation();
    onChildSelect(e, childCert);
  };

  const handleParentClick = (e: React.MouseEvent) => {
    onClick(e, cert);
  };

  return (
    <li>
      <div
        className={`cursor-pointer border-b border-neutral/75 hover:rounded hover:bg-secondary/25 hover:border-none mr-2 ${
          isSelected ? "bg-secondary/25  border-none rounded " : ""
        }`}
        onClick={handleParentClick}
        onDoubleClick={() => onDoubleClick(cert)}
        onContextMenu={(e) => onContextMenu?.(e, cert)}
      >
        <div className="flex items-center space-x-2">
          {!isFlat && cert.children?.length > 0 ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setOpen(!open);
              }}
            >
              {open ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
            </button>
          ) : (
            <div className="w-4" />
          )}

          {/* Certificate Info */}
          <div className="flex-grow min-w-0">
            <CertificateNode cert={cert} />
          </div>
        </div>
      </div>

      {/* Child certs */}
      {open && cert.children?.length > 0 && (
        <ul className="ml-4 mt-2 space-y-2">
          {cert.children.map((child) => (
            <TreeItem
              key={child.id}
              cert={child}
              selectedIds={selectedIds} // we'll fix selection pass down properly later
              onClick={handleChildClick}
              onDoubleClick={onChildDoubleClick}
              onChildSelect={handleChildClick}
              onChildDoubleClick={onChildDoubleClick}
              onContextMenu={onContextMenu}
            />
          ))}
        </ul>
      )}
    </li>
  );
}
