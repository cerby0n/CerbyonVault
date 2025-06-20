import { Trash2, Upload } from "lucide-react";
import CertUploadModal from "../modals/CertUploadModal";
import { useCertUpload } from "../../hooks/useCertUpload";



type ListHeaderProps<Item> = {
  searchTerm: string;
  setSearchTerm: React.Dispatch<React.SetStateAction<string>>;
  selectedItems: Item[];
  handleDeleteSelected: () => void;
  fetchType:()=>void;
  clearSelection:()=>void;
};

export default function ListHeader<ItemType>({
  searchTerm,
  setSearchTerm,
  selectedItems,
  handleDeleteSelected,
  fetchType,
  clearSelection,
}: ListHeaderProps<ItemType>) {
  const { showCertUploadModal, handleUploadButton, closeCertModal,setShowCertUploadModal } =
    useCertUpload();

  const uploadBtn = () =>{
    clearSelection()
    handleUploadButton()
  }

  return (
    <div className="flex items-center justify-between p-6 bg-base-100 rounded top-0">
      {/* Password Modal for PFX Files */}
      {showCertUploadModal && <CertUploadModal closeCertModal={closeCertModal} setShowCertUploadModal={setShowCertUploadModal} fetchFunction={fetchType} />}
      <input
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="input block w-72 focus:outline-none"
      />
      <div className="flex items-center gap-5">
        <div className="flex justify-end">
          {selectedItems.length > 0 && (
            <button
              className="btn btn-error text-error-content rounded"
              onClick={handleDeleteSelected}
            >
              <Trash2/> Delete
            </button>
          )}
        </div>
        <div>
          <button
            className="btn btn-primary font-bold"
            onClick={uploadBtn}
          >
            <Upload className=" text-primary-content" strokeWidth={2.5} />
            Upload
          </button>
        </div>
      </div>
    </div>
  );
}
