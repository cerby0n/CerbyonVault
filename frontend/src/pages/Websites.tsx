import Sidebar from "../components/Sidebar";
import WebsitesList from "../components/WebsitesList";

export default function Websites() {
  return (
    <div className="flex min-h-screen overflow-hidden">
      <div className="shrink-0">
        <Sidebar />
      </div>
      <div className="flex min-w-0 w-full p-4 pl-0">
        <WebsitesList />
      </div>
    </div>
  );
}
