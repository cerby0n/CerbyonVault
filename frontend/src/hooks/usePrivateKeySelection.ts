import { useState, useCallback } from "react";
import { PrivateKey } from "../types";

// Custom hook for managing PrivateKey selection
export const usePrivateKeySelection =  () => {
  const [selectedItems, setSelectedItems] = useState<PrivateKey[]>([]);
  const [lastSelectedItem, setLastSelectedItem] = useState<PrivateKey | null>(null);
  const [isSidePanelVisible, setIsSidePanelVisible] = useState(false);

  const handleSelect = (item: PrivateKey, e: React.MouseEvent, keys: PrivateKey[]) => {
    const isShiftClick = e.shiftKey;
    const isCtrlClick = e.ctrlKey;

    if (isShiftClick && lastSelectedItem) {
      
      const lastIndex = keys.findIndex(key => key.id === lastSelectedItem.id);
      const currentIndex = keys.findIndex(key => key.id === item.id);

      if (lastIndex >= 0 && currentIndex >= 0) {
        const startIndex = Math.min(lastIndex, currentIndex);
        const endIndex = Math.max(lastIndex, currentIndex);
        const itemsToSelect = keys.slice(startIndex, endIndex + 1);
        
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

  const handleOpenDetails = (item: PrivateKey) => {
    console.log("Opening details for private key:", item);
    
  };

  const clearSelection = useCallback(() => {
    setSelectedItems([]); 
    setIsSidePanelVisible(false); 
    setLastSelectedItem(null);
  }, []);

  return { selectedItems, handleSelect, clearSelection, handleOpenDetails, isSidePanelVisible };
};
