import { useState } from "react";

export const useCertUpload =()=>{
    const [showCertUploadModal,setShowCertUploadModal] = useState(false)


    const handleUploadButton = () => {
        setShowCertUploadModal(true)
      };
    
    const closeCertModal = ()=>{
        setShowCertUploadModal(false)
    }
      return{
        handleUploadButton,
        closeCertModal,
        showCertUploadModal,
        setShowCertUploadModal
      };


} 
