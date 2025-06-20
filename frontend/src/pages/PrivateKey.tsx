import PrivateKeyList from "../components/PrivateKeyList";
import Sidebar from "../components/Sidebar";

export default function PrivateKey() {
  return (
    <div className="flex min-h-screen overflow-hidden">
      <div className="shrink-0">
        <Sidebar />
      </div>
      <div className="flex min-w-0 w-full p-4 pl-0">
        <PrivateKeyList />
      </div>
    </div>
  );
}
