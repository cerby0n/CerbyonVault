import { DashboardStats } from "../components/DashboardStats";
import Sidebar from "../components/Sidebar";

export default function Dashboard() {
  return (
    <div className="flex min-h-screen overflow-hidden">
      <div className="shrink-0">
        <Sidebar />
      </div>
      <div className="flex min-w-0 w-full p-4 pl-0">
        <DashboardStats />
      </div>
    </div>
  );
}
