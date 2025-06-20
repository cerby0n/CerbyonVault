import { useCallback, useState } from "react";
import { Certificate } from "../types";

// Custom hook for managing item selection
export const useSelection = <T extends Certificate>() => {
  const [selectedItems, setSelectedItems] = useState<T[]>([]);
  const [lastSelectedItem, setLastSelectedItem] = useState<T | null>(null);
  const [isSidePanelVisible, setIsSidePanelVisible] = useState(false)


  const handleSelect = (item: T, e: React.MouseEvent, certificates: T[]) => {
    const isShiftClick = e.shiftKey;
    const isCtrlClick = e.ctrlKey;

    if (isShiftClick && lastSelectedItem) {
      
      const lastIndex = certificates.findIndex(cert => cert.id === lastSelectedItem.id);
      const currentIndex = certificates.findIndex(cert => cert.id === item.id);

      if (lastIndex >= 0 && currentIndex >= 0) {
        const startIndex = Math.min(lastIndex, currentIndex);
        const endIndex = Math.max(lastIndex, currentIndex);
        const itemsToSelect = certificates.slice(startIndex, endIndex + 1);
        
        setSelectedItems(itemsToSelect);

        if (startIndex !== lastIndex || endIndex !== lastIndex) {
          setIsSidePanelVisible(false); 
        } else {
          setIsSidePanelVisible(true); 
        }
      }
    } else if (isCtrlClick) {
      
      const isItemSelected = selectedItems.some(selected => selected.id === item.id);

      if (!isItemSelected) {
        
        setSelectedItems(prevSelected => [...prevSelected, item]);
        setIsSidePanelVisible(false);
      } else {
        
        setSelectedItems(prevSelected => prevSelected.filter(selected => selected.id !== item.id));
        setIsSidePanelVisible(true);
      }
    } else {
      
      const isItemSelected = selectedItems.some(selected => selected.id === item.id);

      if (!isItemSelected) {
        setSelectedItems([item]); 
        setIsSidePanelVisible(true); 
      } else {
        setSelectedItems(prevSelected => prevSelected.filter(selected => selected.id !== item.id)); 
        setIsSidePanelVisible(false);
      }
    }

    setLastSelectedItem(item);
  };

  const handleOpenDetails = (item: Certificate) => {
    console.log("Opening details for item:", item);

  };

  const clearSelection = useCallback(() => {
    setSelectedItems([]);
    setIsSidePanelVisible(false);
    setLastSelectedItem(null); // Reset the last selected item
  }, []);


  return { selectedItems, handleSelect, clearSelection, handleOpenDetails,isSidePanelVisible };
};
